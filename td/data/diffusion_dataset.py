import random

import numpy as np
import torch.nn.functional as F
from absl import logging
from torch.utils.data import get_worker_info, IterableDataset

from td.environments import environments
from td.learning.tokenizer import Tokenizer
from td.learning.evaluation import OneStepEvaluator
from td.samplers import ConstrainedRandomSampler
from td.samplers.mutator import (
    forward_process,
    forward_process_with_guards,
    forward_process_with_path,
)


class TreeDiffusionDataset(IterableDataset):
    def __init__(
        self,
        batch_size,
        env_name: str,
        min_steps,
        max_steps,
        max_sequence_length,
        min_primitives,  # for random mix samples
        max_primitives,  # for random mix samples
        forward_mode,
        target_observation,
        current_observation,
        random_mix,
        sample_min_primitives=None,  # for original sample (before mutating)
        sample_max_primitives=None,  # for original sample (before mutating)
        selection_max_primitives=None,  # max size selected for mutation
        replacement_max_primitives=None,  # max size of mutation replacement
        path_max_primitives=None,  # max mutations each path step
    ):
        self._env = None
        self._env_name = env_name
        self._batch_size = batch_size
        self._min_steps = min_steps
        self._max_steps = max_steps
        self._max_sequence_length = max_sequence_length
        self._min_primitives = min_primitives
        self._sample_min_primitives = sample_min_primitives or min_primitives
        self._sample_max_primitives = sample_max_primitives or max_primitives
        self._selection_max_primitives = selection_max_primitives or max_primitives
        self._replacement_max_primitives = replacement_max_primitives or max_primitives
        self._path_max_primitives = path_max_primitives or max_primitives
        self._max_primitives = max_primitives
        self._forward_mode = forward_mode
        self._target_observation = target_observation
        self._current_observation = current_observation
        self._random_mix = random_mix

    def _produce_batch(self):
        try:

            def sample_fn():
                return self._sampler.sample(
                    self._env.grammar.sample_start_symbol,
                    min_primitives=self._sample_min_primitives,
                    max_primitives=self._sample_max_primitives,
                )

            target_expressions = []

            while len(target_expressions) < self._batch_size:
                expression = self._env.sample_non_empty(sample_fn)
                target_expressions.append(expression)

            steps = [
                random.randint(self._min_steps, self._max_steps)
                for _ in range(self._batch_size)
            ]
            if self._forward_mode == "path":
                training_examples = [
                    forward_process_with_path(
                        expression,
                        step,
                        self._env.grammar,
                        self._sampler,
                        min_primitives=self._min_primitives,
                        max_primitives=self._max_primitives,
                        selection_max_primitives=self._selection_max_primitives,
                        replacement_max_primitives=self._replacement_max_primitives,
                        path_max_primitives=self._path_max_primitives,
                        p_random=self._random_mix,
                    )
                    for expression, step in zip(target_expressions, steps)
                ]
            elif self._forward_mode == "guards" or self._forward_mode == "guards_full":
                training_examples = [
                    forward_process_with_guards(
                        expression,
                        step,
                        self._env.grammar,
                        self._sampler,
                        full_intersection=self._forward_mode == "guards_full",
                    )
                    for expression, step in zip(target_expressions, steps)
                ]
            else:
                training_examples = [
                    forward_process(
                        expression,
                        step,
                        self._env.grammar,
                        self._sampler,
                        self._selection_max_primitives,
                        self._replacement_max_primitives,
                    )
                    for expression, step in zip(target_expressions, steps)
                ]

            target_images = [
                (
                    self._env.compile(expression)
                    if not self._target_observation
                    else self._env.compile_observation(expression)
                )
                for expression in target_expressions
            ]
            mutated_images = [
                (
                    self._env.compile(expression)
                    if not self._current_observation
                    else self._env.compile_observation(expression)
                )
                for expression, _ in training_examples
            ]
            # print target examples and trianing examples
            # for i in range(len(target_expressions)):
            # print("Target:  ", target_expressions[i])
            # print("\n")
            # print("Training:", training_examples[i][0])
            # print("\n\n")
        except Exception as e:
            # print("Restarting")
            logging.warning(f"Failed to compile: {e}")
            logging.exception(e)
            return self._produce_batch()
        tokenized = []
        context_tokens_mask = []
        for mutated_expression, reverse_mutation in training_examples:
            # print(f"Mutation: {reverse_mutation}")
            context_tokens, positions = self._tokenizer._tokenize_one(
                mutated_expression, translate_positions=True
            )
            start_position = positions[reverse_mutation.start]

            start_position_token = self._tokenizer.position_token(start_position)
            replacement_tokens = self._tokenizer._tokenize_one(
                reverse_mutation.replacement
            )

            tokens = (
                context_tokens
                + [self._tokenizer.sos_token, start_position_token]
                + replacement_tokens
                + [self._tokenizer.eos_token]
            )

            if len(tokens) > self._tokenizer.max_sequence_length:
                logging.warning(
                    f"Token sequence too long {len(tokens)} > {self._tokenizer.max_sequence_length}. Skipping batch."
                )
                tokenized.append(None)
                context_tokens_mask.append(None)
                break

            tokenized.append(
                tokens
                + [self._tokenizer.pad_token]
                * (self._tokenizer.max_sequence_length - len(tokens))
            )
            context_tokens_mask.append(
                [0] * (len(context_tokens) + 1)
                + [1] * (len(tokens) - len(context_tokens) - 1)
                + [0] * (self._tokenizer.max_sequence_length - len(tokens))
            )

        if any(t is None for t in tokenized):
            print("Retrying")
            return self._produce_batch()
        # print each original expression, mutated expression pair
        # for i in range(len(target_expressions)):
        #     print("Original:", target_expressions[i])
        #     print("\n")
        #     print("Mutated:", training_examples[i][0])
        #     print("\n\n")
        return (
            np.array(tokenized),
            np.array(context_tokens_mask),
            np.array(target_images).transpose(0, 3, 1, 2),
            np.array(mutated_images).transpose(0, 3, 1, 2),
            np.array(steps),
        )

    def __iter__(self):
        worker_info = get_worker_info()

        if worker_info is not None:
            np.random.seed(worker_info.id)
            random.seed(worker_info.id)

        if self._env is None:
            self._env = environments[self._env_name]()

        self._sampler = ConstrainedRandomSampler(self._env.grammar)
        self._tokenizer = Tokenizer(
            self._env.grammar,
            max_token_length=self._max_sequence_length,
            max_sequence_length=self._max_sequence_length,
        )
        while True:
            yield self._produce_batch()

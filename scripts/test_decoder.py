import torch
import numpy as np
from td.learning.constrained_decoding import sample_model_kv
from td.data.diffusion_dataset import TreeDiffusionDataset
from td.environments.htmlcss import HTMLCSS
from td.learning.gpt import TransformerConfig, TreeDiffusion
from td.learning.tokenizer import Tokenizer
from td.learning.evaluation import OneStepEvaluator
from td.samplers import ConstrainedRandomSampler
from td.samplers.mutator import random_mutation

def main():
    env = HTMLCSS()
    sampler = ConstrainedRandomSampler(env.grammar)
    max_sequence_length = 128
    tokenizer = Tokenizer(
        env.grammar,
        max_token_length=max_sequence_length,
        max_sequence_length=max_sequence_length,
    )
    config = TransformerConfig(
        vocab_size=tokenizer.vocabulary_size,
        n_layer=2,
        n_head=2,
        n_embd=4,
        max_seq_len=max_sequence_length,
    )
    model = TreeDiffusion(config)

    target_expression = sampler.sample(
        start=env.grammar.sample_start_symbol,
        min_primitives=2,
        max_primitives=24
    )

    print(f"{target_expression=}")

    mutation = random_mutation(
        target_expression, env.grammar, sampler,
        selection_max_primitives=12,
        replacement_max_primitives=12
    )
    mutated_expression = mutation.apply(target_expression)
    print("mutated")
    target_images = np.array([env.compile(target_expression)])
    target_images = (torch.tensor(target_images)
        .float()
        .permute(0, 3, 1, 2)
    )
    print("compiled")
    batch_predicted_reverse_mutations = sample_model_kv(
        model, env, tokenizer, 
        current_expressions=[mutated_expression], 
        target_images=target_images, 
        temperature=0.1
    )

    print(batch_predicted_reverse_mutations)

if __name__ == "__main__":
    main()

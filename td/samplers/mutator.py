from typing import Sequence, Tuple, List

from td.grammar import Grammar
from td.samplers import ConstrainedRandomSampler
from lark import Token, Tree, Visitor
import random
from dataclasses import dataclass


@dataclass(frozen=True)
class Mutation(object):
    start: int
    end: int
    replacement: str
    edit_probs: List[Tuple[int, int, float]] = None

    def apply(self, expression: str) -> str:
        return expression[: self.start] + self.replacement + expression[self.end :]

    def reverse(self, expression: str) -> "Mutation":
        new_start = self.start
        new_end = self.start + len(self.replacement)
        return Mutation(new_start, new_end, expression[self.start : self.end])

    def pretty(self, expression: str) -> str:
        pointer = (
            " " * self.start
            + "^" * (self.end - self.start)
            + " --> "
            + self.replacement
        )
        return expression + "\n" + pointer

    def shift_other(self, other: "Mutation") -> "Mutation":
        """How should another mutation be shifted when this mutation is applied?"""

        if other.start < self.start:
            return other

        if other.start >= self.end:
            return Mutation(
                other.start + len(self.replacement) - (self.end - self.start),
                other.end + len(self.replacement) - (self.end - self.start),
                other.replacement,
            )

        raise ValueError("Mutations overlap!")


class AddParents(Visitor):
    def __default__(self, tree):
        for subtree in tree.children:
            if isinstance(subtree, Tree):
                subtree.parent = tree


class CountPrimitives(Visitor):
    def __init__(self, primitives) -> None:
        super().__init__()
        self._primitives = primitives

    def __default__(self, tree):
        self_count = int(tree.data in self._primitives) if isinstance(tree, Tree) else 0
        count = self_count
        for child in tree.children if isinstance(tree, Tree) else [tree]:
            if isinstance(child, Tree):
                count += child.primitive_count
            elif isinstance(child, Token) and child.type in self._primitives:
                count += 1
        if isinstance(tree, Tree):
            tree.primitive_count = count
        return count


def nodes_with_max_primitives(tree: Tree, primitive_set, max_primitives):
    CountPrimitives(primitive_set).visit(tree)
    return [
        x
        for x in tree.iter_subtrees()
        if hasattr(x, "primitive_count") and x.primitive_count <= max_primitives
    ]


import re


def is_star_node(node):
    return isinstance(node.data, str) and re.match(r"^__\w+_star_\d+$", node.data)


def find_nth_child(tree, n):
    if n < 0:
        return None
    if not tree.children:
        return None

    current_tree = tree
    while True:
        if len(current_tree.children) > n:
            return current_tree.children[n]
        elif len(current_tree.children) == 1 and is_star_node(current_tree.children[0]):
            current_tree = current_tree.children[0]
        else:
            return None


def random_mutation(
    expression: str,
    grammar: Grammar,
    sampler: ConstrainedRandomSampler,
    selection_max_primitives: int = 2,
    replacement_max_primitives: int = 2,
    max_attempts_difference: int = 100,
) -> Mutation:
    tree = grammar.parse(expression)
    AddParents().visit(tree)

    candidates = nodes_with_max_primitives(
        tree, grammar.primitives, selection_max_primitives
    )
    candidate_primitive_counts = [x.primitive_count for x in candidates]
    unique_primitive_counts = list(set(candidate_primitive_counts))
    candidate_primitive_count = random.choice(unique_primitive_counts)
    candidates_with_count = [
        x for x in candidates if x.primitive_count == candidate_primitive_count
    ]
    candidates = candidates_with_count

    while True:
        if not candidates:
            return None

        candidate = random.choice(candidates)

        if (
            not hasattr(candidate, "parent")
            # or grammar.names_to_symbols[candidate.parent.data] == grammar.start_symbol
        ):
            # We have the root, sample a new expression.
            start = 0
            end = len(expression)
            sub_expression = expression[start:end]
            start_symbol = grammar.sample_start_symbol
        else:
            parent = candidate.parent
            start = candidate.meta.start_pos
            end = candidate.meta.end_pos

            sub_expression = expression[start:end]
            self_child_index = parent.children.index(candidate)
            matched = grammar.tree_matcher.match_tree(parent, parent.data)
            matched_child = matched.children[
                0 if self_child_index >= len(matched.children) else self_child_index
            ]
            if matched_child is None:
                raise ValueError("Could not find matched child")
                # candidates.remove(candidate)
                # continue
            rule_name = matched_child.data
            options = grammar.nonterminals[rule_name]

            if len(options) <= 1:
                candidates.remove(candidate)
                continue

            start_symbol = grammar.names_to_symbols[rule_name]

        attempts = 0
        while True:
            replacement_expression = sampler.sample(
                start_symbol,
                min_primitives=0,
                max_primitives=replacement_max_primitives,
            )
            attempts += 1

            if replacement_expression != sub_expression:
                break

            if attempts > max_attempts_difference:
                candidates.remove(candidate)
                break

        mutation = Mutation(start, end, replacement_expression)
        return mutation


def apply_all_mutations(expression: str, mutations: Sequence[Mutation]) -> str:
    """Apply a sequence of mutations to an expression.

    Mutations are applied in order, and each mutation is shifted to account for the previous mutations.

    Args:
        expression: The original expression.
        mutations: A sequence of mutations to apply.

    Returns:
        The expression after all mutations have been applied.
    """

    mutations = [m for m in mutations]
    current = expression
    while mutations:
        mut = mutations.pop(0)
        mutations = [mut.shift_other(m) for m in mutations]
        current = mut.apply(current)
    return current


def one_step_path_mutations(
    exprA: str,
    exprB: str,
    grammar: Grammar,
    sampler: ConstrainedRandomSampler,
    max_primitives: int = 2,
    truncate_nonzero: bool = False,
    small_sources: bool = True,
) -> List[Mutation]:
    """Given two expressions, find a sequence of mutations that transforms one into the other.

    Note that these will be all the mutations that can applied in the first step. You may need to call this function multiple times to get the full transformation.

    Args:
        exprA: The source expression.
        exprB: The target expression.
        grammar: The grammar to use.
        sampler: The sampler to use.
        max_primitives: The maximum number of primitives that can be added in a single mutation. This defines how "small" the mutations are.
        truncate_nonzero: If True, the target expression will always have at most 0 primitives.
        small_sources: If False, allow the source expression to be larger than max_primitives.

    Returns:
        A sequence of mutations that transform the source expression into the target expression.
    """

    primitive_counter = CountPrimitives(grammar.primitives)
    parent_adder = AddParents()

    def prepare_tree(expression):
        tree = grammar.parse(expression)
        primitive_counter.visit(tree)
        parent_adder.visit(tree)
        return tree

    def node_eq(nodeA, nodeB):
        if isinstance(nodeA, Token) and isinstance(nodeB, Token):
            return nodeA.value == nodeB.value
        if len(nodeA.children) != len(nodeB.children):
            return False

        # if len(nodeA.children) == 1:
        #     return node_eq(nodeA.children[0], nodeB.children[0])

        return nodeA.data == nodeB.data

    def treediff(treeA, treeB, expressionA, expressionB):

        if isinstance(treeA, Token) and isinstance(treeB, Token):
            if treeA.value == treeB.value:
                return []
            else:
                return [Mutation(treeA.start_pos, treeA.end_pos, treeB.value)]

        if isinstance(treeA, Token) or isinstance(treeB, Token):
            return [
                Mutation(
                    start=(
                        treeA.start_pos
                        if not isinstance(treeA, Tree)
                        else treeA.meta.start_pos
                    ),
                    end=(
                        treeA.end_pos
                        if not isinstance(treeA, Tree)
                        else treeA.meta.end_pos
                    ),
                    replacement=(
                        expressionB[treeB.start_pos : treeB.end_pos]
                        if not isinstance(treeB, Tree)
                        else expressionB[treeB.meta.start_pos : treeB.meta.end_pos]
                    ),
                )
            ]

        if (isinstance(treeA, Tree) and isinstance(treeB, Tree)) and node_eq(
            treeA, treeB
        ):
            # This node is the same, recurse on children.
            rv = []
            for childA, childB in zip(treeA.children, treeB.children):
                rv.extend(treediff(childA, childB, expressionA, expressionB))
            return rv
        else:
            source_passes = (
                small_sources and getattr(treeA, "primitive_count", 1) <= max_primitives
            ) or (not small_sources)
            target_passes = (
                getattr(treeB, "primitive_count", 1) <= max_primitives
                and not truncate_nonzero
            ) or (truncate_nonzero and getattr(treeB, "primitive_count", 1) <= 0)
            if source_passes and target_passes:
                return [
                    Mutation(
                        start=treeA.meta.start_pos,
                        end=treeA.meta.end_pos,
                        replacement=expressionB[
                            treeB.meta.start_pos : treeB.meta.end_pos
                        ],
                    )
                ]
            elif not truncate_nonzero:
                if not hasattr(treeA, "parent"):
                    start_symbol = grammar.sample_start_symbol
                else:
                    parent = treeA.parent
                    self_child_index = parent.children.index(treeA)

                    matched = grammar.tree_matcher.match_tree(parent, parent.data)
                    # matched_child = find_nth_child(matched, self_child_index)
                    matched_child = matched.children[
                        (
                            0
                            if self_child_index >= len(matched.children)
                            else self_child_index
                        )
                    ]
                    rule_name = matched_child.data
                    start_symbol = grammar.names_to_symbols[rule_name]
                b = expressionB[treeB.meta.start_pos : treeB.meta.end_pos]
                if treeB.primitive_count <= max_primitives:
                    return [
                        Mutation(
                            start=treeA.meta.start_pos,
                            end=treeA.meta.end_pos,
                            replacement=b,
                        )
                    ]

                min_primitives = min(max_primitives, treeB.primitive_count)
                new_expression = sampler.sample(
                    start_symbol,
                    min_primitives=min_primitives,
                    max_primitives=max_primitives,
                )
                try:
                    tightening_diffs = one_step_path_mutations(
                        new_expression,
                        b,
                        grammar,
                        max_primitives,
                        truncate_nonzero=True,
                    )
                except: # might not be a start point for language
                    tightening_diffs = []

                new_expression = apply_all_mutations(new_expression, tightening_diffs)
                if not hasattr(treeA.meta, "start_pos"):
                    print(f"treeA does not has start pos:\n{treeA.pretty()}")
                return [
                    Mutation(
                        start=treeA.meta.start_pos,
                        end=treeA.meta.end_pos,
                        replacement=new_expression,
                    )
                ]

        return []

    try:
        treeA = prepare_tree(exprA)
    except Exception as e:
        print(f"\n\nError in prepare_tree: {exprA=}, {exprB=}\n\n")
        raise e
    try:
        treeB = prepare_tree(exprB)
    except Exception as e:
        print(f"\n\nError in prepare_tree: {treeA=} {exprA=}, {exprB=}\n\n")
        raise e
    return treediff(treeA, treeB, exprA, exprB)


def find_path(
    source: str,
    target: str,
    grammar: Grammar,
    sampler: ConstrainedRandomSampler,
    max_primitives: int = 2,
    max_steps: int = 50,
):
    current = source
    path = []
    steps = 0

    while current != target:
        current_mutations = one_step_path_mutations(
            current, target, grammar, sampler, max_primitives
        )
        random.shuffle(current_mutations)
        current_mutations.sort(
            key=lambda m: (m.end - m.start) + len(m.replacement), reverse=True
        )

        while current_mutations:
            mut = current_mutations.pop(0)
            path.append(mut)
            new_current = mut.apply(current)
            if new_current == target:
                return path
            current_mutations = [mut.shift_other(m) for m in current_mutations]
            current = new_current

        steps += 1

        if steps > max_steps:
            return None
    return path


def forward_process(
    expression: str,
    num_steps: int,
    grammar: Grammar,
    sampler: ConstrainedRandomSampler,
    selection_max_primitives=2,
    replacement_max_primitives=2,
) -> Tuple[str, Mutation]:
    current_expression = expression
    reverse_mutation = None
    for i in range(num_steps):
        mutation = random_mutation(
            current_expression,
            grammar,
            sampler,
            selection_max_primitives,
            replacement_max_primitives,
        )
        if mutation is None:
            continue
            # raise ValueError("No mutation found")

        # Premature optimization is the root of all evil.
        if i == num_steps - 1:
            reverse_mutation = mutation.reverse(current_expression)
        current_expression = mutation.apply(current_expression)

    return current_expression, reverse_mutation


def forward_process_with_path(
    expression: str,
    num_steps: int,
    grammar: Grammar,
    sampler: ConstrainedRandomSampler,
    min_primitives: int = 2,  # for random mode sampling
    max_primitives: int = 7,  # for random mode sampling
    path_max_primitives: int = 2,  # max size of path mutations
    selection_max_primitives: int = 2,  # max size of selected nodes to mutate
    replacement_max_primitives: int = 2,  # max size of mutation replacements
    p_random: float = 0.2,
    force_mode: str = None,
    return_full_path: bool = False,
) -> Tuple[str, Mutation]:
    mode = (
        force_mode
        if force_mode is not None
        else ("random" if random.random() < p_random else "mutated")
    )
    if mode == "random":
        mutated_expression = sampler.sample(
            grammar.sample_start_symbol, min_primitives, max_primitives
        )
    elif mode == "mutated":
        mutated_expression, _ = forward_process(
            expression,
            num_steps,
            grammar,
            sampler,
            selection_max_primitives,
            replacement_max_primitives,
        )
    else:
        raise ValueError("Invalid mode")
    path = find_path(
        mutated_expression, expression, grammar, sampler, path_max_primitives
    )

    if path is None or len(path) == 0:
        return forward_process_with_path(
            expression,
            num_steps,
            grammar,
            sampler,
            min_primitives,
            max_primitives,
            path_max_primitives,
            selection_max_primitives=selection_max_primitives,
            replacement_max_primitives=replacement_max_primitives,
            p_random=p_random,
            force_mode=None,
            return_full_path=return_full_path,
        )

    path_step = random.randint(0, len(path) - 1)
    target_mutation = path[path_step]
    path_to_execute = path[:path_step]

    return_expression = mutated_expression

    for mutation in path_to_execute:
        return_expression = mutation.apply(return_expression)

    if return_full_path:
        return return_expression, target_mutation, path[path_step:]

    return return_expression, target_mutation


def _intersects(interval1, interval2):
    # Intersects or if one contains the other
    a, b = interval1
    c, d = interval2
    return (a <= c <= b) or (c <= a <= d)


def forward_process_with_guards(
    expression: str,
    num_steps: int,
    grammar: Grammar,
    sampler: ConstrainedRandomSampler,
    full_intersection: bool = False,
    max_tries: int = 20,
) -> Tuple[str, Mutation]:
    current_expression = expression
    guards = []

    for i in range(num_steps):
        attempts = 0
        while True:
            mutation = random_mutation(current_expression, grammar, sampler)
            if not any(
                (
                    s <= mutation.start < e or s <= mutation.end < e
                    if not full_intersection
                    else _intersects((mutation.start, mutation.end), (s, e))
                )
                for s, e in guards
            ):
                break

            if (attempts := attempts + 1) > max_tries:
                break

        if attempts > max_tries:
            break

        # Premature optimization is the root of all evil.
        reverse_mutation = mutation.reverse(current_expression)

        if mutation is None:
            break

        current_expression = mutation.apply(current_expression)

        delta = len(mutation.replacement) - (mutation.end - mutation.start)
        guards = [
            (
                s + delta if s > mutation.start else s,
                e + delta if s > mutation.start else e,
            )
            for s, e in guards
            if not _intersects((mutation.start, mutation.end), (s, e))
        ]
        guards.append((mutation.start, mutation.start + len(mutation.replacement)))

    return current_expression, reverse_mutation

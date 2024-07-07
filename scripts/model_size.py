from td.learning.gpt import TreeDiffusion
from td.environments.htmlcss import HTMLCSS
import os
import pickle
import random
import uuid

import numpy as np
import torch
import torch.nn.functional as F
from absl import app, flags, logging
from torch.utils.data import DataLoader

import wandb
from td.data.diffusion_dataset import TreeDiffusionDataset
from td.environments import environments
from td.learning.gpt import TransformerConfig, TreeDiffusion
from td.learning.tokenizer import Tokenizer
from td.learning.evaluation import OneStepEvaluator
from td.samplers import ConstrainedRandomSampler

def format_parameters_count(n_params):
    if n_params >= 1e9:
        return f'{n_params / 1e9:.2f} billion'
    elif n_params >= 1e6:
        return f'{n_params / 1e6:.2f} million'
    elif n_params >= 1e3:
        return f'{n_params / 1e3:.2f} thousand'
    return str(n_params)

def format_memory_size(size_bytes):
    if size_bytes >= 1e9:
        return f'{size_bytes / 1e9:.2f} GB'
    elif size_bytes >= 1e6:
        return f'{size_bytes / 1e6:.2f} MB'
    elif size_bytes >= 1e3:
        return f'{size_bytes / 1e3:.2f} KB'
    return f'{size_bytes} bytes'

def main():
    env = HTMLCSS()
    max_sequence_length = 3000
    tokenizer = Tokenizer(
        env.grammar,
        max_token_length=max_sequence_length,
        max_sequence_length=max_sequence_length,
    )
    model = TreeDiffusion(
        TransformerConfig(
            vocab_size=tokenizer.vocabulary_size,
            max_seq_len=tokenizer.max_sequence_length,
            n_layer=10,
            n_head=16,
            n_embd=512,
        ),
        input_channels=env.compiled_shape[-1],
        image_model_name="nf_resnet26",
    )
    image_model = model.image_encoder
    transformer = model.transformer

    # Calculate parameters and memory usage
    image_model_params = sum(p.numel() for p in image_model.parameters() if p.requires_grad)
    transformer_params = sum(p.numel() for p in transformer.parameters() if p.requires_grad)

    # Memory calculation assumes single precision (32-bit float)
    bytes_per_param = 4
    image_model_memory = image_model_params * bytes_per_param
    transformer_memory = transformer_params * bytes_per_param

    print(f'Image Model Parameters: {format_parameters_count(image_model_params)}')
    print(f'Transformer Parameters: {format_parameters_count(transformer_params)}')
    print(f'Estimated Image Model Memory Usage: {format_memory_size(image_model_memory)}')
    print(f'Estimated Transformer Memory Usage: {format_memory_size(transformer_memory)}')

if __name__ == '__main__':
    main()

When working with GitHub Actions you will sooner or later need
passwords, API keys and other secrets.

The goal of this exercise is to create a GitHub Action that simply
reads a secret and "tries" to print it in the pipeline logs; tries,
because GitHub blocks secret printing by default and outputs asterisks
in its place (redacted).

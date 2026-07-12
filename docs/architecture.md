# Architecture

## High-Level Design

Double Clap
    |
    V
Clap Detection Service
    |
    V
CLAP Core Engine
    |
    +-------------------+
    |                   |
    V                   V
Voice Engine       Information Services
                        |
         +--------------+-------------+
         |              |             |
         V              V             V
      Weather      System Info      Forex
                                         |
                                         V
                                   Music Player

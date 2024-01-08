# RPG Stat Analyzer

A collection of utilities for calculating and visualizing statistics of dice rolls in rpg-games

## Goal

This project aims to provide a library for calculating rpg-game dice rolls, tools for visualizing them and ultimately a way to define a system of dice rolls coresponding statsheets for entities in game and analyze interactions between those in the specified system.

## Modules

The modules to be developed as part of this project are:
- rpg_dice_stats: a library for intuitively writing dice rules in python and analyzing their statistical distributions
- dsa_dice_stats: a library providing dice rules for DSA
- dnd_dice_stats: a library providing dice rules for DnD
- rpg_dice_vis: a library for visualizing these dice rolls
- rpg_system_defs: a library for defining stat sheets and corresponding dice rules for an rpg system and analyzing them. Builds on rpg_dice_stats.
# RAG-FITNESS-ASSISTANT

Staying consistent with fitness routines is challenging,
especially for beginners. Gyms can be intimidating, and personal
trainers aren't always available.

The Fitness Assistant provides a conversational AI that helps
users choose exercises and find alternatives, making fitness more
manageable.

## Project overview

The Fitness Assistant is a RAG application designed to assist
users with their fitness routines.

The main use cases include:

1. Exercise Selection: Recommending exercises based on the type
   of activity, targeted muscle groups, or available equipment.
2. Exercise Replacement: Replacing an exercise with suitable
   alternatives.
3. Exercise Instructions: Providing guidance on how to perform a
   specific exercise.
4. Conversational Interaction: Making it easy to get information
   without sifting through manuals or websites.

## Dataset

The dataset used in this project contains information about
various exercises, including:

- **Exercise Name:** The name of the exercise (e.g., Push-Ups, Squats).
- **Type of Activity:** The general category of the exercise (e.g., Strength, Mobility, Cardio).
- **Type of Equipment:** The equipment needed for the exercise (e.g., Bodyweight, Dumbbells, Kettlebell).
- **Body Part:** The part of the body primarily targeted by the exercise (e.g., Upper Body, Core, Lower Body).
- **Type:** The movement type (e.g., Push, Pull, Hold, Stretch).
- **Muscle Groups Activated:** The specific muscles engaged during
  the exercise (e.g., Pectorals, Triceps, Quadriceps).
- **Instructions:** Step-by-step guidance on how to perform the
  exercise correctly.

The dataset was generated using ChatGPT and contains 207 records. It serves as the foundation for the Fitness Assistant's exercise recommendations and instructional support.

## Running it

You can run it in a virtual environment
This project made use of `uv`

```bash
    uv python install
```

you can create and spin up a virrtual environment using the follow command, of you are on windows

```bash
    uv venv
    source .venv/Scripts/activate
```

## Ingestion

## Ragflow

## Evaluation

To check the code for retrival, you can check out the [Fitness_Assistant.ipynb](Fitness_Assistant.ipynb) notebook

### Retrival

The basic approach without using boosting functionality in minsearch givs the following result:
{'hit_rate': 0.851207729468599, 'mrr': 0.7854543363239016}

The improved version with an optimized boosting paramater gave:
{'hit_rate': 0.8473429951690822, 'mrr': 0.8062905452035889}

The best boosting parameters

```bash
    boost = {
        'exercise_name': 2.11,
        'type_of_activity': 1.46,
        'type_of_equipment': 0.65,
        'body_part': 2.65,
        'type': 1.31,
        'muscle_groups_activated': 2.54,
        'instructions': 0.74
    }
```
### monitoring

### Containerization

### Reproducibility

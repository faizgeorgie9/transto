# Transto

Transto is an algorithm-based recommendation system designed to assist users in selecting the most suitable intercity transportation and food options based on cost and travel time considerations.

This project was developed to fulfill the requirements of the **Design and Analysis of Algorithms** course.

## Project Background
Choosing an appropriate mode of intercity transportation is a common challenge, especially when users must consider multiple factors such as travel time, cost, and route complexity. With various transportation options available, including trains, buses, and airplanes, decision-making often becomes inefficient.

Transto addresses this problem by implementing algorithmic approaches to provide effective and optimized recommendations.

## Algorithm Overview
This project applies different algorithms based on travel scenarios:

- **Greedy Algorithm**  
  Used for non-transit ticket selection to achieve fast computation with low memory usage.  
  Time complexity: **O(E)**

- **Uniform Cost Search (UCS)**  
  Used for transit-based journeys to find the optimal combination of routes based on cumulative cost.  
  Time complexity: **O(2E)**

The combination of these algorithms allows the system to balance efficiency and optimality depending on user needs.

## Features
- Transportation mode recommendation (train, bus, airplane)
- Food recommendation based on selected routes
- Support for transit and non-transit journeys
- Algorithm-based decision optimization
- Modular algorithm implementation

## Technologies Used
- Programming Language: **Python**
- Algorithms: Greedy, Uniform Cost Search (UCS)
- Concepts: Graph traversal, cost optimization, algorithm complexity analysis

## How to Run the Program

1. Ensure Python is installed on your system (Python 3.8 or later is recommended).

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
3. Navigate to the project directory.
4. Run the main application file:
    python app.py

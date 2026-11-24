# Community Bakery Simulation

## 1. Project Overview

The Community Bakery Simulation is a Python-based application that models the weekly operations of a small bakery. It allows a bakery manager to make operational decisions involving workforce allocation, product sales, ingredient purchases, stock management and customer advance orders.

The simulation processes weekly trading activities while maintaining financial records, ingredient inventory and order fulfilment information. It applies validation rules to ensure that decisions comply with available resources and the bakery's operating constraints.

The project is developed using Python and its standard library, with an object-oriented structure that separates the main simulation logic, product definitions, inventory management, validation and file replay functionality.

## 2. Main Features

The application provides the following functionality:

- **Weekly trading simulation:** Runs a bakery simulation for a configurable period of 1–12 weeks.
- **Workforce management:** Supports workforce decisions within the permitted range of one to three employees.
- **Product sales:** Manages sales of loaves, buns and slices according to weekly demand.
- **Ingredient management:** Tracks flour, butter and fruit inventory, including stock consumption, storage capacity and spoilage.
- **Financial management:** Calculates sales revenue, employee wages, weekly rent, ingredient purchasing costs and closing cash balances.
- **Decision validation:** Checks sales, purchases, workforce allocation and resource availability before processing a trading week.
- **Advance order management:** Supports customer orders with product details, quantities and collection weeks.
- **Order fulfilment:** Processes eligible advance orders and records whether orders are fulfilled or missed.
- **File-based simulation:** Supports JSON scenario and decision files and exports weekly simulation results as JSON.
- **Regression testing:** Includes automated tests for core functionality, validation, calculations and advance-order behaviour.

## 3. Project Structure

The project is organised into separate Python modules to improve maintainability and separation of responsibilities.

| File / Directory | Responsibility |
|---|---|
| `main.py` | Provides the interactive command-line interface and simulation entry point. |
| `bakery.py` | Implements the main bakery simulation and weekly trading calculations. |
| `product.py` | Defines bakery products, recipes, production times and selling prices. |
| `ingredient.py` | Defines ingredient properties, capacities, prices and spoilage rates. |
| `recipeitem.py` | Represents individual ingredient requirements within product recipes. |
| `stock.py` | Manages ingredient inventory, stock updates and spoilage calculations. |
| `validation.py` | Validates numerical inputs, quantities and trading decisions. |
| `order.py` | Defines customer advance orders and their statuses. |
| `orderbook.py` | Stores, validates and manages the complete batch of advance orders. |
| `replay.py` | Loads JSON inputs and executes reproducible simulation runs. |
| `check_stock.py` | Provides a small stock-independence and spoilage demonstration. |
| `API.md` | Documents the Stage 1 public interfaces and expected behaviours. |
| `API_STAGE2.md` | Documents the Stage 2 advance-order interface additions. |
| `data/` | Contains example scenario and decision JSON files. |
| `tests/` | Contains supplied tests and student-developed regression tests. |
| `tests_stage2/` | Contains the supplied Stage 2 public tests. |

## 4. System Design and Responsibilities

The simulation follows an object-oriented design in which each module has a defined responsibility.

The `Bakery` class coordinates weekly trading operations. It uses the product and ingredient catalogues to calculate production requirements, revenue and resource consumption. The `Stock` class manages ingredient quantities, while the validation module checks whether submitted decisions satisfy the simulation rules.

The advance-order functionality is separated into the `Order` and `OrderBook` classes. This separation allows customer orders to be validated, stored and processed independently of the main interactive interface.

The replay module supports repeatable simulations by loading scenario and decision information from JSON files. This enables simulation runs to be reproduced and their weekly results exported for inspection.

## 5. Requirements

The project requires:

- Python 3.11 or later.
- No external Python packages are required.
- A terminal or command-line environment.
- All supplied Python modules must remain together in the project directory.

## 6. Running the Application

Open a terminal in the directory containing `main.py`.

### Run the interactive simulation

```bash
python main.py
```

The application prompts the user to specify the simulation duration, workforce, product sales and ingredient purchases.

### Run a simulation using JSON files

```bash
python main.py --scenario data/example.json --decisions data/example_decisions.json --output output/run.json
```

The command uses:

- `--scenario`: Specifies the JSON file containing simulation conditions and weekly demand.
- `--decisions`: Specifies the JSON file containing weekly operational decisions.
- `--output`: Specifies the destination for the generated weekly simulation results.

The output directory is created automatically if it does not already exist.

## 7. Running the Tests

The project uses Python's built-in `unittest` framework.

### Run the Stage 1 and student regression tests

```bash
python -m unittest discover -s tests -v
```

### Run the Stage 2 public tests

```bash
python -m unittest discover -s tests_stage2 -v
```

### Run an individual student test module

```bash
python -m unittest tests.student.test_issue1_history -v
```

The tests cover areas including history preservation, input validation, financial calculations and advance-order functionality.

A successful test run indicates that the behaviours covered by the executed tests passed. It does not independently establish that every possible simulation scenario is correct.

## 8. Simulation Outputs

Each completed trading week produces a record containing relevant operational and financial information, including:

- Week number and workforce allocation.
- Opening and closing cash balances.
- Revenue, wages, rent and ingredient purchasing costs.
- Product sales and advance-order sales.
- Opening, consumed, discarded, purchased and closing stock.
- Production time used.
- Fulfilled and missed advance-order identifiers.
- Bankruptcy status.

All monetary values are represented in integer pence to support consistent financial calculations.

## 9. Development Stages

The project was developed in two stages:

**Stage 1 – Core Bakery Simulation**

The initial stage focused on the main bakery operations, including product sales, ingredient inventory, workforce allocation, financial calculations, decision validation and weekly history management.

**Stage 2 – Advance Order Management**

The second stage extended the simulation to support advance customer orders. It introduced order validation, order-book management, weekly fulfilment processing and additional information in the weekly simulation records while preserving the existing Stage 1 functionality.

## 10. Version Control

The project uses Git for version control and development tracking.

The following development tags identify the completed stages:

- `stage1-complete`
- `stage2-complete`

The Git repository maintains the development history and provides a record of the implementation stages.

## 11. Conclusion

The Community Bakery Simulation provides a modular Python application for modelling bakery operations over multiple trading weeks. It combines inventory management, financial calculations, input validation and advance customer-order processing within a structured object-oriented design. The application also supports reproducible JSON-based simulation runs and automated testing, providing a foundation for evaluating the behaviour and reliability of the implemented system.
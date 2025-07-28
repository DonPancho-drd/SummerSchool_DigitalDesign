# Project breakdown

In this repository, you can find MOSFET circuit designs created using LTspice. To view the .asc, .asy, or .plt files, you must first install LTspice.

## Repository Structure

### `/initial`
MOSFET characteristics research and behavioral analysis

### `/seq` and `/comb`
- Sequential and combinational logic circuits
- Commonly used logic gates with schematic symbols

### `/test` 
Circuit functionality verification tests  
*(Note: Not all test files are included in this repository)*

### `/rom`
Idealized ROM model for LTspice simulations

### `/fadder` and '/verify'
Various 1-bit full adder implementations:
- Verified using test scripts in `/verify`

## Program Counter Implementation
A functional 4-bit Program Counter design consisting of:
- 4-bit register
- 16×8 ROM
- 4-bit adder (for increment operations) 
- 4 multiplexers controlled by `branch` signal

## Usage
1. Clone this repository
2. Open desired `.asc` files in LTspice
3. Run simulations or examine circuit designs





# 🧮 Half Adder and Full Adder Design

This README describes the architecture and implementation of **half adders** and **full adders**, key components in digital arithmetic logic used for binary addition.

---

## 🔹 Half Adder

A **half adder** adds two 1-bit binary numbers `A` and `B`. It produces two outputs:

- **Sum (`S`)**
- **Carry-out (`Cout`)**

Because the sum of two 1-bit numbers can be 0, 1, or 2, two bits are required to represent the result.

### Truth Table

| A | B | Cout | S |
|---|---|------|---|
| 0 | 0 |  0   | 0 |
| 0 | 1 |  0   | 1 |
| 1 | 0 |  0   | 1 |
| 1 | 1 |  1   | 0 |

### Logic Expressions

```
S    = A ⊕ B
Cout = A · B
```

---

## 🔹 Full Adder

A **full adder** adds three 1-bit inputs: `A`, `B`, and a carry-in (`Cin`). It produces:

- **Sum (`S`)**
- **Carry-out (`Cout`)**

This allows cascading multiple full adders to construct multi-bit adders.

### Generate/Propagate/Kill Signals

These auxiliary signals help optimize adder designs:

- **Generate (`G`)**: Carry is generated regardless of `Cin` → `G = A · B`
- **Propagate (`P`)**: Carry is propagated if one input is 1 → `P = A ⊕ B`


### Logic Expressions

```
S    = _A_BCin ⊕ A_B_Cin ⊕ _AB_Cin ⊕ ABCin = A ⊕ B ⊕ Cin = P ⊕ Cin
Cout = AB + ACin + BCin = MAJ(A, B, Cin)
```

---

## 🔧 Gate-Level and Transistor-Level Design

### Full Adder

- Uses **32 transistors**:
  - 6 for inverters
  - 10 for majority gate
  - 16 for 3-input XOR

### Optimized Full Adder

Reduces transistor count to **28** using **mirror adder** topology.

- Reuses `Cout` in `S` logic:
```
S = (A ⊕ B) ⊕ Cin = f(Cout)
```
- **Symmetric layout** with identical nMOS/pMOS networks
- Better layout uniformity and performance

---

## 🔹 Full N-bit Adder

### 🔸 Ripple Carry Adder (RCA)

The simplest form of a parallel adder is the **Ripple Carry Adder**, built by cascading `n` full adders (FAs), where each carry-out feeds the next carry-in.

- **Hardware Complexity**: Linear in `n`
- **Worst-Case Delay**: Also proportional to `n`, due to carry propagation ripple

> 🔧 To speed up ripple carry adders, it is crucial to minimize the **delay from carry-in (`ci`) to carry-out (`ci+1`)** in each full adder.

### Implementation

Full adders can be realized using:

- **Basic logic gates**: AND, OR, XOR (as in standard gate-level design)
- **MOSFET-based circuits**: Including **pass transistor** logic for faster carry propagation

---

## 🔸 Manchester Carry Chain (Manchester Adder)

To improve propagation speed, ripple carry adders often use a **Manchester carry chain**, implemented with **CMOS transmission gates** and pass transistors.

### Behavior Summary

- When `xi = yi = 0`: `ci+1 = 0` via nMOS path to ground
- When `xi = yi = 1`: `ci+1 = 1` via pMOS path to Vdd
- When `xi ≠ yi`: Carry-in (`ci`) is directly propagated to `ci+1` through a transmission gate

This behavior results in **faster carry propagation** than in basic logic gate implementations.


---

## ⏭️ Carry Skip Adders

In a **Ripple Carry Adder**, carry propagation is typically the bottleneck in speed. A carry propagates through the *i-th* full adder (**FA**) **only when**:

```
xi ≠ yi   ⇒   xi ⊕ yi = 1
```

This XOR condition is denoted as:

```
pi = xi ⊕ yi
```

A **carry will propagate through an entire block** of FAs if **all** the `pi` signals within the block are `1`. This is known as the **carry propagation condition** for the block.

---

### ⚙️ Carry Skip Technique

A **Carry Skip Adder (CSA)** improves upon the ripple carry design by:

- Dividing the adder into **multiple blocks** of full adders
- Inserting a **carry skip circuit** between each block

When the carry propagation condition holds (i.e., all `pi = 1` within the block), the carry can **bypass** the entire block rather than rippling through each bit.

> 🔁 This **"skipping"** dramatically reduces the worst-case delay for carry propagation, especially for large adders.

---

## ⚡ Carry-Lookahead Adders (CLA)

Large **Ripple-Carry Adders** are slow due to carry signals that must ripple through **every bit** from least significant to most significant position.

To overcome this, the **Carry-Lookahead Adder (CLA)**:

- Divides the adder into **blocks**
- Uses logic to **quickly determine the carry-out** of each block as soon as the carry-in is known

This allows the adder to “**look ahead**” instead of waiting for each bit to complete its addition.

---

### 🧱 Block-Based Structure

A typical CLA structure:

- A 32-bit CLA may be divided into **eight 4-bit blocks**
- Each block contains:
  - A 4-bit ripple-carry adder
  - Lookahead logic for carry computation

> 🧩 This modular approach improves speed and maintainability

---

### 🧮 Generate and Propagate Logic

Each bit position computes two key signals:

- **Generate (Gi)**: Carry is produced regardless of carry-in
  `Gi = Ai & Bi`

- **Propagate (Pi)**: Carry-in is passed to carry-out
  `Pi = Ai | Bi`

#### Carry-Out Computation

The carry-out for column *i*:

```text
Ci = Gi + Pi ⋅ Ci−1
```

---

### 🛠️ CLA Block Structure

Each block:

- Computes 1-bit **Pi** and **Gi**
- Aggregates them into multi-bit **Pi:j** and **Gi:j**
- Feeds into an **AND/OR gate** to compute the carry-out of the block

> This structure drastically reduces the carry delay vs ripple-carry designs.

---

### 🧭 Carry Propagation Path

In a 32-bit CLA (with 4-bit blocks):

1. Compute all Pi and Gi in **parallel**
2. Compute all Pi:j and Gi:j for each block
3. Carry-in travels:
   - `Cin → C3 → C7 → C11 ... → C31`
   - Each hop through one AND/OR gate

This means the carry path is **logarithmic in delay**, not linear.

---


## ⚡ Prefix Adders

**Prefix Adders** take the generate/propagate logic of Carry-Lookahead Adders (CLA) even further — enabling **ultra-fast addition** by computing carries for all positions in **logarithmic time** using tree-like structures.

---

### 🧠 Key Idea

Instead of computing carries linearly from right to left, prefix adders **combine generate and propagate signals hierarchically**:

- First, compute G and P for **pairs of columns**
- Then for **blocks of 4**, then **8**, then **16**, and so on
- Until each column knows whether a carry will reach it from column -1 (Cin)

---

### 🧮 Sum Computation

Once carry-in `Ci−1` is known, the **sum bit** at position *i* is:

```text
Si = Ai ⊕ Bi ⊕ Ci−1           (5.7)
```

To compute `Ci−1` fast:

- Define a **virtual column -1**:
  - `G−1 = Cin`
  - `P−1 = 0`

So:

```text
Ci−1 = Gi−1:−1
```

This means: there will be a carry into column *i* if the block from column -1 to *i−1* **generates a carry**.

Hence, Equation (5.7) becomes:

```text
Si = Ai ⊕ Bi ⊕ Gi−1:−1
```

---

### 📊 Prefix Signals

To enable fast computation:

- We compute **block generate prefixes**:
  `G−1:−1, G0:−1, G1:−1, ..., GN−2:−1`

- And **block propagate prefixes**:
  `P−1:−1, P0:−1, P1:−1, ..., PN−2:−1`

These are used to determine which positions **receive a carry**.

---

## 🔚 Summary

Prefix Adders are:

- Faster than Ripple-Carry and CLA
- Structured to compute **all carries simultaneously**
- The core of **modern high-speed arithmetic units**

> Prefix adders showcase how **parallelism and hierarchical logic** can dramatically speed up computation in digital systems.

---

## 📘 Reference

- "CMOS VLSI Design: A Circuits and Systems Perspective"
- "VLSI Handbook"
- "Digital design" by Harris

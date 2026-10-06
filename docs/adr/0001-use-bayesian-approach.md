# ADR-0001: Use Bayesian Approach for GDI

## Status
Accepted

## Context
GDI sebelumnya dirumuskan sebagai penjumlahan linear sederhana. Namun,
sistem geothermal bersifat kompleks dan penuh ketidakpastian.

## Decision
Menggunakan pendekatan Bayesian untuk memodelkan GDI sebagai distribusi
probabilitas, bukan skalar tunggal.

## Consequences
- (+) Menghormati ketidakpastian (honest about uncertainty)
- (+) Bisa di-update dengan data baru
- (-) Membutuhkan komputasi lebih berat
- (-) Perlu keahlian Bayesian inference

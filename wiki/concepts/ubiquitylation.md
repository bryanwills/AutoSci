---
title: "Ubiquitylation"
aliases: ["ubiquitination", "ubiquitin conjugation", "Ub modification"]
tags: [post-translational-modification, ubiquitin, protein-degradation, signalling]
maturity: stable
key_papers: [ubiquitin-ligases-oncogenic-transformation-cancer-therapy]
first_introduced: ""
date_updated: 2026-04-30
related_concepts: [ubiquitin-ligase-e3]
---

## Definition

Ubiquitylation is the covalent attachment of ubiquitin (a 76-residue protein) to a substrate protein, almost always via an isopeptide bond between ubiquitin's C-terminal glycine carboxylate and a lysine ε-amino group on the substrate (or, less commonly, on N-terminal amine, cysteine thiol, or serine/threonine hydroxyl). The reaction is carried out by a three-enzyme cascade: an E1 activates ubiquitin in an ATP-dependent manner forming a thioester, an E2 receives ubiquitin onto its active-site cysteine, and an [[ubiquitin-ligase-e3]] (E3) catalyzes transfer of ubiquitin from E2 to substrate.

## Intuition

Phosphorylation flips a binary on/off bit on a residue. Ubiquitylation writes a small folded protein onto the substrate, and that protein can itself be ubiquitylated to build a chain of variable length and topology. Different chain shapes are read by different downstream proteins, so ubiquitylation behaves more like a typed pointer than a binary modification: the type encodes the destination (proteasome, lysosome, signalling complex, nucleus) while the substrate identity encodes which protein is being routed.

## Formal notation

Ubiquitin chain types, by linkage:

- **Monoubiquitylation** — single Ub on one lysine; regulates localization, complex assembly, transcription, DNA repair.
- **Multi-monoubiquitylation** — multiple substrate lysines, each carrying one Ub.
- **K48 polyubiquitin** — the canonical proteasomal degradation signal. Substrates with chains of ≥ 4 K48-linked Ub are recognized by the 26S proteasome.
- **K63 polyubiquitin** — non-degradative; signals in DNA damage response (RNF8/RNF168 chromatin code), NF-κB activation, kinase activation (for example, AKT activation by SCF–SKP2), endocytic trafficking.
- **K11 polyubiquitin** — APC/C-driven mitotic substrate degradation (cyclin B, securin); also ER-associated degradation.
- **M1 (linear) polyubiquitin** — assembled by LUBAC (HOIP/HOIL-1L/SHARPIN); inflammatory signalling.
- **K6, K27, K29, K33** — atypical linkages; roles still being characterized; involved in mitophagy (parkin generates K6/K11/K48 mixed chains), DNA damage, and protein quality control.
- **Branched / mixed chains** — single chain combining multiple linkages; tunable signal.

Reverse reaction: deubiquitylating enzymes (DUBs; ~100 in humans, families USP, UCH, OTU, MJD, JAMM, MINDY, ZUFSP) cleave isopeptide bonds and edit chain topology.

## Variants

This is a foundational PTM with no major sub-mechanisms — chain topology and reader UBDs constitute the variation. Closely related modifications include:

- **NEDDylation** — attachment of NEDD8 (ubiquitin-like); activates cullin–RING E3s.
- **SUMOylation** — attachment of SUMO; non-degradative regulation of localization, transcription, DNA repair.
- **ISGylation, FAT10ylation, UFMylation, ATG12/ATG8** — other ubiquitin-like modifiers with distinct cascades.

## Comparison

Ubiquitylation differs from phosphorylation in scale (one ubiquitin is ~8 kDa vs one phosphate ~80 Da), reversibility kinetics, and downstream readout (UBD-bearing reader proteins vs phospho-reader domains). It overlaps functionally with autophagy, which clears entire organelles via ubiquitin-tagged adaptors (p62/SQSTM1, NBR1, OPTN). Both proteasomal and autophagic pathways draw on ubiquitin tags, with extensive crosstalk: proteasomes can be cleared by autophagy, and autophagy substrates can route to proteasomes when autophagy is impaired.

## When to use

Invoke when describing any selective protein degradation, non-degradative regulation by Ub chains (DNA damage response, NF-κB, AKT activation, endocytic sorting), the design of PROTAC molecules and molecular glues, the unfolded protein response, or autophagy-proteasome crosstalk.

## Known limitations

- Chain-topology readout is incompletely mapped: many UBDs are promiscuous, and the cellular concentration and competition between readers is hard to model.
- Quantitative ubiquitin proteomics is technically demanding (di-Gly remnant profiling captures K-linkages but loses topology and dynamics).
- The substrate of any given E3/DUB is rarely fully enumerated, so reasoning about which protein an E3 perturbation will affect is uncertain.

## Open problems

- A predictive code mapping (substrate × E3 × cellular state) → (chain topology × downstream fate).
- Single-molecule readouts of chain topology in vivo.
- Therapeutic exploitation of non-degradative ubiquitylation arms (K63, K11, mono-Ub).
- Quantitative dissection of ubiquitin-pool sharing between proteasomal degradation, autophagy, and signalling.

## Key papers

- [[ubiquitin-ligases-oncogenic-transformation-cancer-therapy]] — Senft, Qi & Ronai, Nat Rev Cancer 2018; reviews how ubiquitylation deregulation drives cancer.

## My understanding

Ubiquitylation is the foundational PTM the wiki should treat as the substrate (no pun intended) for almost every protein-stability and signalling claim downstream. Drug-design papers (PROTACs, molecular glues, MDM2 antagonists), structural biology papers (E3-substrate complexes, ubiquitin chain topology), and cancer-genomics papers (FBXW7, VHL, BRCA1, SPOP, MDM2 amplifications) all share this concept as their floor. Distinguishing it from the ligase concept ([[ubiquitin-ligase-e3]]) lets us link claims about *the modification* (chain topology, readers, dynamics) separately from claims about *who writes it* (specific E3s and their substrate networks).

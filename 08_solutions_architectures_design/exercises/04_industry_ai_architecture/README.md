# Cross-industry AI architectures (draw.io workshop)

Architecture workshop from module 08, section 3 (reference architectures): no code,
only design. The deliverable is `cross_industry_architectures.drawio`, built block by
block during the lesson, with one page per industry scenario:

- Banking fraud detection: POS/ATM ingress through a secure-zone datacenter, local GPU
  inference on the transaction path (millisecond budget), block/allow decision, audit log.
- Medical imaging: TAC/MRI source, edge server segmentation, radiologist workstation
  with overlay, human-in-the-loop sign-off producing the final report, feedback into a
  training DB. The diagram separates a machine layer (automation, privacy) from a human
  layer (decision and HITL).
- Manufacturing quality control: smart camera on the production line, edge AI device
  (Jetson-class) driving a PLC/robot for real-time part separation, deferred QA review
  building a golden dataset for on-premise retraining.

Open the file with [draw.io / diagrams.net](https://www.diagrams.net/) (desktop or
browser). The three scenarios map one-to-one onto the cross-industry lecture (slides
`13_cross_industry_architectures_and_human_in_the_loop.pptx`) and notes 03 and 08.

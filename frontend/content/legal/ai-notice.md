# AI and Evidence Notice

**Effective {{effective}}**

{{product}} uses automated web search and third-party language models. This notice explains what that means for the outputs you see.

## How outputs are produced

1. A language model drafts a research plan, which you can edit.
2. The Service searches the web and your uploaded documents and stores what it retrieves.
3. A language model extracts individual claims from that material.
4. A language model checks each claim against specific passages and must quote the exact words it relied on. If the quote is not in the passage, the check is discarded.
5. Fixed rules, not the model, decide each claim's status: Supported, Partially supported, Contradicted, Unsupported or Missing data.
6. Scores and the overall verdict are calculated by fixed rules from those statuses. Financial projections are calculated in code from stated assumptions.

## What the labels mean

- **Supported** means a high-quality source, or two independent sources, state the claim. It does not mean the claim is true.
- **Relevant** sources that do not state a claim never count as support.
- **Model estimate** marks a financial assumption that no source provided. Replace it with your own figure where you can.

## Evidence you add

You can add a link, pasted text or one of your PDFs to any claim. It is checked in the same way, with an exact quote, and labelled "Added by user" everywhere it appears, including exports. Links are fetched by our servers only when you ask, and only from public web addresses. You can also dispute a claim; a disputed claim counts as no evidence in the decision until the dispute is cleared.

## Refreshes and the sample report

A refresh repeats a question with the same reviewed plan and searches again. The comparison of the two runs is calculated, not written by a model: claims are matched by word overlap, sources by web address, and the verdict and base case are compared figure by figure. A monthly refresh only runs if you turn it on for a report, and each one uses a run from your workspace's monthly allowance.

The public sample report is labelled as such. Unless its label says it is a recorded real run, its sources and figures are made up to show how a report reads and must not be relied on.

## Limitations

Language models can misread text and search engines can return outdated, biased or wrong pages. Sources may be paywalled, incomplete or change after retrieval. Coverage depends on what search can find. Always read the cited extracts before relying on a figure, and treat outputs as a starting point for your own analysis.

Outputs are not financial, investment, legal or tax advice. See our [Terms of Service](/legal/terms).

## Your content and model providers

Your questions, the retrieved passages and the text of documents you select for a run are sent to our language-model provider to generate outputs. We use paid API services whose terms do not allow the provider to use your content to train or improve its models. See the [subprocessor list](/legal/subprocessors).

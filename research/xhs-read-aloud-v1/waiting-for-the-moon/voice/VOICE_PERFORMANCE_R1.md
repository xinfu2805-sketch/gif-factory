# VOICE-PERFORMANCE-R1 | 2026-11-11 UTC

## Outcome

**FIRST_DIVERGENCE: Azure Speech F0 resource access is unavailable in this
runtime.** No Azure resource ID, region, subscription key, account session, F0
SKU or remaining quota can be verified. The environment has no matching
credential variable names, `az`/`spx` executable, or Azure CLI profile.
A single unauthenticated HEAD to an Azure Speech voice-list endpoint was stopped
by the environment's CONNECT proxy with HTTP 403. This is a proxy observation,
not evidence that Azure Speech itself is down or that an account was rejected.
No authenticated synthesis request was made. The endpoint was not retried.

Consequently **zero new WAVs** and no listening ZIP exist for R1. No paid API,
proxy workaround, full video or story edit was attempted. The prior Kokoro
`af_sol` auditions passed signal checks but the user rejected their bedtime
storytelling quality. `VOICE_REVIEW`, `READ_ALOUD_PASS`, and `PUBLISH_READY`
remain **BLOCKED**.

## Frozen audition text and unexecuted style plan

The exact page 03 and 07 English text is in `../story.json`; no text was changed.
Microsoft lists both `en-US-AriaNeural` and `en-US-JennyNeural` as female voices.
Its voice table lists `empathetic`, `sad`, `friendly`, and `whispering` for Aria;
Jenny supports `sad`, `friendly`, and `whispering`, but not `empathetic`.
If a lawful, reachable audition resource is supplied later, test page 03 with
Aria `empathetic` and Jenny `sad`; test page 07 with each voice's `friendly`
style and a restrained `whispering` closing phrase. These are **plans, not
validated performance settings**. A connected-story audition is deferred.

## Quota and rights boundary

Microsoft publishes 0.5 million neural TTS characters/month for Free F0;
that does not establish this account's tier, balance or authorization.
Microsoft's current Azure Product Terms explicitly grant use of prebuilt neural
voice audio output, including commercial use, to **paid-tier TTS customers
only**. Therefore F0 audition output cannot be marked cleared for Xiaohongshu
release based on these terms. Any later publication needs a separately verified
license basis; this task did not authorize a paid tier.

## Alternative feasibility, not executed

| Route | Conditions before research auditions | Publication boundary |
| --- | --- | --- |
| ElevenLabs | An authorized account, reachable service and available free quota; separately check the selected voice and terms. No call made. | Official free plan is noncommercial with attribution. It is not cleared as a commercial publication source; a paid plan is outside this task's authorization. |
| Chatterbox Nano | Official ResembleAI model weights must be reachable or lawfully imported offline, with MIT model-card license retained; verify local CPU/RAM, dependencies and an authorized reference voice before running. No download or synthesis made. | MIT model card is promising, but the exact voice/reference rights and real listening quality still require review. |

## Sources checked

- [Azure Speech quickstart: resource key and region](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/get-started-text-to-speech)
- [Microsoft voice and style support](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support?tabs=text-to-speech)
- [Azure Speech F0 pricing](https://azure.microsoft.com/en-us/pricing/details/speech/)
- [Microsoft Azure Product Terms, TTS output rights](https://www.microsoft.com/licensing/terms/en-US/product/MicrosoftAzure/MCA)
- [ElevenLabs billing and free-tier license](https://elevenlabs.io/docs/overview/administration/billing)
- [Official ResembleAI Chatterbox Nano model card](https://huggingface.co/ResembleAI/chatterbox-nano)

Next executable step: obtain a reachable, explicitly authorized audition
resource with confirmed tier and quota, or lawfully import the official offline
model and a permitted voice reference. Then generate the four raw audition WAVs
and submit them for the user's hearing; no gate passes by technical checks alone.

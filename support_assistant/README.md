\# Zepto Policy Support Assistant



\## Overview



This module implements a Zepto policy support assistant using LangGraph, ChromaDB, Sentence Transformers, Pydantic, and FastAPI.



The assistant classifies user queries and routes them through different LangGraph nodes. Zepto policy questions use semantic retrieval from a local ChromaDB collection, while general questions use a direct response path.



The default graded configuration uses:



MOCK\_LLM=1



This allows the project to run without an external LLM API key.



\## Policy Corpus



The local knowledge base contains 8 Zepto policy documents covering:



1\. Delivery

2\. Returns and refunds

3\. Membership

4\. Order tracking

5\. Cancellation

6\. Damaged, spoiled, or missing items

7\. Gift cards

8\. Customer support



\## Embeddings and Vector Database



The project uses the local Sentence Transformers model:



all-MiniLM-L6-v2



The documents are embedded and stored in a persistent ChromaDB collection.



To create or refresh the vector database:



python ingest.py



Expected result:



Documents embedded successfully.

Documents stored: 8



\## LangGraph Architecture



The workflow contains three nodes:



1\. classify\_intent

2\. retrieve\_and\_answer

3\. direct\_answer



Flow:



User Query

&#x20;   |

&#x20;   v

classify\_intent

&#x20;   |

&#x20;   +----------------------+

&#x20;   |                      |

policy\_question      general\_question

&#x20;   |                      |

&#x20;   v                      v

retrieve\_and\_answer   direct\_answer

&#x20;   |                      |

&#x20;   +----------+-----------+

&#x20;              |

&#x20;             END



Policy questions retrieve relevant policy documents from ChromaDB before producing a response.



General questions follow the direct-answer path.



\## Prompt Design



The policy prompt contains:



\- Role

\- Context

\- Task

\- Output format

\- Length constraint

\- Negative constraints

\- Few-shot example



The assistant is instructed to use only retrieved Zepto policy context and not invent unsupported policy information.



\## Mock LLM Mode



Mock mode is enabled by default:



MOCK\_LLM=1



In mock mode:



\- Intent classification is deterministic.

\- Policy questions still perform real ChromaDB retrieval.

\- The answer is generated deterministically from the top retrieved chunk.

\- General questions use the direct-answer route.

\- No external LLM API is required.



\## Optional Real LLM Mode



The project also contains an optional real-LLM path.



Set:



MOCK\_LLM=0



and configure the required API key before running.



The real-LLM response is validated using Pydantic. If validation fails, the application retries up to two additional times before returning a clear error response.



The graded baseline does not require this mode.



\## Response Schema



The `/ask` endpoint returns:



```json

{

&#x20; "answer": "string",

&#x20; "sources": \["document\_id"],

&#x20; "confidence": 1.0

}S


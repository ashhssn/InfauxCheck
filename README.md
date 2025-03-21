# InfauxCheck

InfauxCheck is an LLM Agent-powered application to combat misinformation. The application leverages RAG to provide users with a way to verify the credibility of information they come across on the web.


### Technologies Demonstrated

* Agent
* Fine-tuning an LLM (BERT) for downstream tasks
* Retrieval Augmented Generation (RAG) for information retrieval
* Prompt Engineering
* Optical Character Recognition

### Tools used

* Huggingface Transformers
* PyTorch
* LangChain
* PaddleOCR
* Flask

### Additional Features

* Codebase modularization
* Well-documented codebase
* Leveraging on GenAI tools (ChatGPT, GitHub Copilot) to improve development efficiency

## Installation

1. Install `requirements.txt`. Recommened to use a virtual environment.

    ```bash
    pip install -r requirements.txt
    ```

2. Generate the `Chroma` vector database by running the notebook found under `notebooks/embedding_vectordb.ipynb`.

3. Download the pretrained BERT classifier model [here](https://drive.google.com/file/d/14LsoD1eWix4xPHDJLRluzkIN44CgrbgM/view?usp=sharing) and put it under a folder in root `checkpoints/`.


## Usage

In the root directory, simply run the following command:

```bash
python src/main.py
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.
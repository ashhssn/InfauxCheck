# InfauxCheck

InfauxCheck is an LLM Agent-powered application to combat misinformation. The application leverages RAG to provide users with a way to verify the credibility of information they come across on the web. 

## Installation

1. Install `requirements.txt`. Be smart and use a virtual environment.

    ```bash
    pip install -r requirements.txt
    ```

2. Generate the `Chroma` vector database by running the notebook found under `notebooks/embedding_vectordb.ipynb`.

3. Download the pretrained BERT classifier model [here]() and put it under a folder `checkpoints/`.


## Usage

In the root directory, simply run the following command:

```bash
python src/main.py
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.
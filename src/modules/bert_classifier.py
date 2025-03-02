import torch
import torch.nn as nn
from torch.utils.data import Dataset
import transformers
from transformers import BertModel, BertTokenizer


class CustomDataset(Dataset):

    def __init__(self, data, tokenizer, max_len, training=False):
        self.data = data
        self.tokenizer = tokenizer
        self.max_len = max_len
        self.type = type(self.data)
        self.training = training
        if self.training:
            # in training, data is in dict format and consists of labels
            self.features = [self.data['text']]
            self.labels = [self.data['label']]
        else:
            self.features = [self.data]

    def __len__(self):
        return len(self.features)

    def __getitem__(self, idx):
        feature = str(self.features[idx])
        if self.training:
            label = self.labels[idx]

        encoding = self.tokenizer.encode_plus(
            feature,
            add_special_tokens=True,
            max_length=self.max_len,
            return_token_type_ids=False,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt'
        )
        if self.training:
            return {
                'review_text': feature,
                'input_ids': encoding['input_ids'].flatten(),
                'attention_mask': encoding['attention_mask'].flatten(),
                'targets': torch.tensor(label, dtype=torch.float)
            }
        else:
                        return {
                'review_text': feature,
                'input_ids': encoding['input_ids'].flatten(),
                'attention_mask': encoding['attention_mask'].flatten()
            }
    
class BERTModel(nn.Module):

    def __init__(self, numcl=1):
        super().__init__()
        self.model = BertModel.from_pretrained("bert-base-uncased", torch_dtype=torch.float, attn_implementation="sdpa", return_dict=False)
        self.drop = nn.Dropout(p=0.4)
        self.fc = nn.Linear(self.model.config.hidden_size, numcl)

    def forward(self, input_ids, attn_mask):
        _, pooled_output = self.model(
            input_ids=input_ids,
            attention_mask=attn_mask)
        output = self.drop(pooled_output)
        return self.fc(output)
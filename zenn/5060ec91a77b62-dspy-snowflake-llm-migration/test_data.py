from datasets import load_dataset

dataset = load_dataset("fancyzhx/amazon_polarity")

for split_name, split_data in dataset.items():
    split_data.to_parquet(f"amazon_polarity_{split_name}.parquet")
    print(f"{split_name}: {len(split_data)} rows saved")

from tqdm import tqdm


def stage_tqdm(items, desc: str):
    return tqdm(items, desc=desc)

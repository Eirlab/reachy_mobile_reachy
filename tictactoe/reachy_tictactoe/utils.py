piece2id = {
    'cube': 1,
    'cylinder': 2,
    'empty': 0,
}

id2piece = {
    v: k for k, v in piece2id.items()
}

piece2player = {
    'cube': 'human',
    'cylinder': 'robot',
    'empty': 'nobody',
}

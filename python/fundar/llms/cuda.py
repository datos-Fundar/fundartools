class CudaDeviceError(Exception):
    ERROR_STR = """No CUDA devices found, they're crucial for this functionality.
                 If you have a CUDA device and is not being detected, please install NVIDIA's CUDA drivers and PyTorch accordingly 
                 by following this instructions https://pytorch.org/get-started/locally/"""
    
    def __init__(self):
        super().__init__(CudaDeviceError.ERROR_STR)

def are_torch_and_cuda_correctly_installed(quiet=True):
    try:
        import torch

        if not torch.cuda.is_available():
            raise CudaDeviceError
        
    except ModuleNotFoundError as e:
        raise ModuleNotFoundError('Torch not installed, please install it from https://pytorch.org/get-started/locally/')
    
    if not quiet:
        print('CUDA and torch are correctly installed.')
import sys
sys.path.append('C:/Users/Ali/Documents/toonity/modules/Hunyuan3D-2')
sys.path.append('C:/Users/Ali/Documents/toonity/inter-systems')
import os
import base64
from io import BytesIO
from PIL import Image
from hy3dgen.shapegen import Hunyuan3DDiTFlowMatchingPipeline
from hy3dgen.texgen import Hunyuan3DPaintPipeline
from hy3dgen.rembg import BackgroundRemover
from hy3dgen.text2image import HunyuanDiTPipeline
import torch

from ModuleBaseClass import ModuleBase

torch.cuda.empty_cache()
torch.cuda.ipc_collect()

SAVE_DIR = './exports'

class HunyuanModule(ModuleBase):
    def __init__(self, name):
        ModuleBase.__init__(self, name)
        self.rembg = BackgroundRemover()

    def load_image_from_base64(self, image):
        return Image.open(BytesIO(base64.b64decode(image)))

    @torch.inference_mode()
    def generate(self, params):
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()
        uid = params["uid"]
        if 'image' in params:
            image = params["image"]
            image = self.load_image_from_base64(image)
            model_path = 'tencent/Hunyuan3D-2'
            self.pipeline_shapegen = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained(model_path)
        else:
            if 'text' in params:
                text = params["text"]
                self.pipeline_imagegen = HunyuanDiTPipeline()
                image = self.pipeline_imagegen(prompt=text)
                del self.pipeline_imagegen
                torch.cuda.empty_cache()
                torch.cuda.ipc_collect()
                model_path = 'tencent/Hunyuan3D-2'
                self.pipeline_shapegen = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained(model_path)
            else:
                raise ValueError("No input image or text provided")

        image = self.rembg(image)
        params['image'] = image
        seed = params.get("seed", 1234)
        params['generator'] = torch.Generator('cuda').manual_seed(seed)
        # params['octree_resolution'] = params.get("octree_resolution", 128)
        # params['num_inference_steps'] = params.get("num_inference_steps", 5)
        # params['guidance_scale'] = params.get('guidance_scale', 5.0)
        # params['mc_algo'] = 'mc'
        mesh = self.pipeline_shapegen(**params)[0]

        save_path = save_file_path = os.path.join(SAVE_DIR, f'{uid}.obj')

        print("shapegen finished")

        del self.pipeline_shapegen
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()

        simplified_mesh = mesh.simplify_quadric_decimation(percent=0.8)
        self.pipeline_tex = Hunyuan3DPaintPipeline.from_pretrained(model_path)
        simplified_mesh = self.pipeline_tex(simplified_mesh, image)
        print("texgen finished")
        simplified_mesh.export(save_path)
        del self.pipeline_tex
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()
        return save_path, uid

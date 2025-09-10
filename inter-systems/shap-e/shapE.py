import torch
import sys
import os
import base64
from io import BytesIO
from PIL import Image
sys.path.append('C:/Users/Ali/Documents/toonity/inter-systems')
from ModuleBaseClass import ModuleBase

from shap_e.diffusion.sample import sample_latents
from shap_e.diffusion.gaussian_diffusion import diffusion_from_config
from shap_e.models.download import load_model, load_config
from shap_e.util.notebooks import create_pan_cameras, decode_latent_images, gif_widget
from shap_e.util.notebooks import decode_latent_mesh



class ShapEModule(ModuleBase):
  def __init__(self, name):
    self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    self.xm = load_model('transmitter', device=self.device)
    self.model = load_model('text300M', device=self.device)
    self.diffusion = diffusion_from_config(load_config('diffusion'))
    ModuleBase.__init__(self, name)

  def load_image_from_base64(self, image):
      return Image.open(BytesIO(base64.b64decode(image)))

  def generate(self, params):
      prompt = params["text"]
      # image = params["image"]
      # image = self.load_image_from_base64(image)
      uid = params["uid"]
      batch_size = 1
      guidance_scale = 15.0
      latents = sample_latents(
          batch_size=batch_size,
          model=self.model,
          diffusion=self.diffusion,
          guidance_scale=guidance_scale,
          model_kwargs=dict(texts=[prompt] * batch_size),
          progress=True,
          clip_denoised=True,
          use_fp16=True,
          use_karras=True,
          karras_steps=512,
          sigma_min=1e-3,
          sigma_max=160,
          s_churn=0,
      )
      for i, latent in enumerate(latents):
          t = decode_latent_mesh(self.xm, latent).tri_mesh()
          with open(f'./exports/{uid}.obj', 'w') as f:
              t.write_obj(f)

      #ModuleBase.generateFromText(self, prompt)

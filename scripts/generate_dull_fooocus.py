#!/usr/bin/env python3
"""
Fooocus 비하인드 코어로 직접 1장 생성 스크립트: 중2 유닛 45 1번 dull
"""
import os
import sys

FOOOCUS_ROOT = "/Users/ijaegwang/Fooocus"
sys.path.insert(0, FOOOCUS_ROOT)
os.chdir(FOOOCUS_ROOT)

import modules.async_worker as worker
from modules.flags import Performance, MetadataScheme, disabled

prompt = (
    "minimalist black and white cartoon line art, cute simple round bald stick figure characters, "
    "one round bald cartoon character in middle looking comically confused and dull, "
    "holding a completely blunt rounded wooden pencil, "
    "another round-headed cartoon stick figure friend next to him scratching his head in disbelief, "
    "thick smooth rounded bold black outlines, doodle drawing style, "
    "pure solid white background, strictly black and white only, no color, no shading"
)
negative_prompt = "color, colors, colored, shading, grayscale, 3d, realistic, blurry, text, watermark"

# Fooocus Task 인자 리스트 순서에 맞춤
# AsyncTask.args 순서 매핑
args = [
    False, # generate_image_grid
    prompt, # prompt
    negative_prompt, # negative_prompt
    ["Fooocus V2", "Fooocus Line Art", "Line Art"], # style_selections
    Performance.SPEED.value, # performance_selection
    "1024*1024", # aspect_ratios_selection
    1, # image_number
    "png", # output_format
    42, # seed
    False, # read_wildcards_in_order
    2.0, # sharpness
    5.0, # cfg_scale
    "DreamShaperXL_Lightning.safetensors", # base_model_name
    "None", # refiner_model_name
    0.5, # refiner_switch
    # 5개의 lora: (enabled, name, weight)
    True, "coloringbook_sdxl.safetensors", 0.85,
    False, "None", 1.0,
    False, "None", 1.0,
    False, "None", 1.0,
    False, "None", 1.0,
    False, # input_image_checkbox
    "uov", # current_tab
    disabled, # uov_method
    None, # uov_input_image
    [], # outpaint_selections
    None, # inpaint_input_image
    "", # inpaint_additional_prompt
    None, # inpaint_mask_image_upload
    True, # disable_preview
    True, # disable_intermediate_results
    True, # disable_seed_increment
    False, # black_out_nsfw
    1.5, # adm_scaler_positive
    0.8, # adm_scaler_negative
    0.3, # adm_scaler_end
    True, # adaptive_cfg
    "dpmpp_2m_sde_gpu", # sampler_name
    "karras", # scheduler_name
    -1, # overwrite_step
    -1, # overwrite_switch
    -1, # overwrite_width
    -1, # overwrite_height
    -1, # overwrite_vary_strength
    -1, # overwrite_upscale_strength
    False, # mixing_image_prompt_and_vary_upscale
    False, # mixing_image_prompt_and_inpaint
    False, # debugging_cn_preprocessor
    False, # skipping_cn_preprocessor
    False, # controlnet_soft_edges
    False, # freeu_enabled
    1.0, 1.0, 1.0, 1.0, # freeu b1, b2, s1, s2
    False, # debug_inpaint_preprocessing
    False, # disable_initial_latent_in_inpaint
    "v2.6", # inpaint_engine
    1.0, # inpaint_denoising_strength
    0.618, # inpaint_respective_field
    False, # enable_advanced_masking_features
    False, # invert_mask_when_generating
    0, # mask_erode_or_dilate
    True, # save_only_final_enhanced_image
    False, # save_metadata_to_images
    MetadataScheme.FOOOCUS.value, # metadata_scheme
    # 4 image prompts
    None, 0.5, 0.6, "ImagePrompt",
    None, 0.5, 0.6, "ImagePrompt",
    None, 0.5, 0.6, "ImagePrompt",
    None, 0.5, 0.6, "ImagePrompt",
]

print("Fooocus AsyncTask 생성 및 실행 중...")
task = worker.AsyncTask(args)
worker.async_tasks.append(task)
worker.handler()

if task.results:
    res = task.results[0]
    print(f"생성 성공! 결과 파일: {res}")
    # assets 및 brain으로 복사
    os.system(f"cp '{res}' /Users/ijaegwang/wordncode/App/English_word/assets/words/dull.png")
    os.system(f"cp '{res}' /Users/ijaegwang/.gemini/antigravity-ide/brain/a965b718-7061-4420-ae74-3d9bec6a9f15/word_dull_fooocus.png")
else:
    print("생성 결과가 없습니다.")

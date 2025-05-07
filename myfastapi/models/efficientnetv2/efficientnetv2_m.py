# Model settings
model_cfg = dict(
    backbone=dict(type='EfficientNetV2', arch='m'),
    neck=dict(type='GlobalAveragePooling'),
    head=dict(
        type='LinearClsHead',
        num_classes=5,
        in_channels=1280,
        loss=dict(type='CrossEntropyLoss', loss_weight=1.0),
        topk=(1, 5),
    ))

# dataloader pipeline
img_norm_cfg = dict(
    mean=[127.5, 127.5, 127.5], std=[127.5, 127.5, 127.5], to_rgb=True)

train_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(
        type='RandomResizedCrop',
        size=224,
        efficientnet_style=True,
        interpolation='bicubic'),
    #dict(type='RandomFlip', flip_prob=0.5, direction='horizontal'),
    dict(type='Normalize', **img_norm_cfg),
    dict(type='ImageToTensor', keys=['img']),
    dict(type='ToTensor', keys=['gt_label']),
    dict(type='Collect', keys=['img', 'gt_label'])
]

val_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(
        type='CenterCrop',
        crop_size=224,
        efficientnet_style=True,
        interpolation='bicubic'),
    dict(type='Normalize', **img_norm_cfg),
    dict(type='ImageToTensor', keys=['img']),
    dict(type='Collect', keys=['img'])
]

# train
data_cfg = dict(
    batch_size = 8,
    num_workers = 2,
    train = dict(
        pretrained_flag = True,
        pretrained_weights = 'datas\efficientnetv2-m_in21k-pre-3rdparty_in1k_20221220-a1013a04.pth',
        freeze_flag = False,
        freeze_layers = ('backbone',),
        epoches = 250,
    ),
    test=dict(
        #ckpt = 'logs/EfficientNetV2/2025-04-01-23-45-05/Val_Epoch171-Acc96.419.pth',#logs\EfficientNetV2\2025-04-06-19-59-56\Val_Epoch229-Acc98.525.pth
        ckpt = 'pth/Val_Epoch229-Acc98.525.pth',
        metrics = ['accuracy', 'precision', 'recall', 'f1_score','confusion'],
        metric_options = dict(
            topk = (1,5),
            thrs = None,
            average_mode='none'
    )
    )
)


# batch 32
# lr = 0.1 *32 /256
# optimizer
optimizer_cfg = dict(
    type='SGD',
    lr=0.001 * 8/256,
    momentum=0.9,
    weight_decay=1e-4)


# optimizer_cfg = dict(
#     type='AdamW',
#     lr=0.001,
#     betas=(0.9, 0.999),
#     eps=1e-8,
#     weight_decay=1e-5,
#     amsgrad=True)


# learning 
lr_config = dict(type='StepLrUpdater', step=4, gamma=0.973, by_epoch=True)
#lr_config = dict(type='StepLrUpdater', warmup='linear', warmup_iters=50, warmup_ratio=0.25,step=[15,30,45])
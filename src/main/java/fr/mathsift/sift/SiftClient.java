package fr.mathsift.sift;

import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.render.fluid.v1.FluidRenderingRegistry;
import net.minecraft.client.color.block.BlockTintSources;
import net.minecraft.client.renderer.block.FluidModel;
import net.minecraft.client.resources.model.sprite.Material;
import net.minecraft.util.ARGB;

public final class SiftClient implements ClientModInitializer {
    @Override public void onInitializeClient() {
        FluidRenderingRegistry.register(SiftFluids.STILL, SiftFluids.FLOWING,
            new FluidModel.Unbaked(
                new Material(SiftMod.id("block/prismatic_tide_still")),
                new Material(SiftMod.id("block/prismatic_tide_flow")),
                new Material(SiftMod.id("block/prismatic_tide_overlay")),
                BlockTintSources.constant(ARGB.opaque(0xFFFFFF))
            ));
    }
}

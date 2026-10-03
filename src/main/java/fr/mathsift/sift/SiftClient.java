package fr.mathsift.sift;

import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.render.fluid.v1.FluidRenderingRegistry;
import net.fabricmc.fabric.api.client.rendering.v1.hud.HudElementRegistry;
import net.fabricmc.fabric.api.client.rendering.v1.hud.VanillaHudElements;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.color.block.BlockTintSources;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.renderer.block.FluidModel;
import net.minecraft.client.resources.model.sprite.Material;
import net.minecraft.core.BlockPos;
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
        HudElementRegistry.attachElementBefore(VanillaHudElements.CHAT,
            SiftMod.id("blue_soul_burn"), SiftClient::renderBlueBurn);
    }

    private static boolean touchingTide(Minecraft minecraft) {
        if (minecraft.player == null || minecraft.level == null) return false;
        var p=minecraft.player;
        double x=p.getX(), y=p.getY(), z=p.getZ();
        var feet=minecraft.level.getFluidState(BlockPos.containing(x,y+.11,z)).getType();
        var waist=minecraft.level.getFluidState(BlockPos.containing(x,y+.74,z)).getType();
        return feet==SiftFluids.STILL || feet==SiftFluids.FLOWING ||
               waist==SiftFluids.STILL || waist==SiftFluids.FLOWING;
    }

    /** Animated blue pixel flames when submerged, without any orange vanilla fire. */
    private static void renderBlueBurn(GuiGraphicsExtractor graphics, DeltaTracker delta) {
        Minecraft minecraft=Minecraft.getInstance();
        if (!minecraft.options.getCameraType().isFirstPerson() ||
            minecraft.player == null || minecraft.player.isSpectator() ||
            !touchingTide(minecraft)) return;
        int width=minecraft.getWindow().getGuiScaledWidth();
        int height=minecraft.getWindow().getGuiScaledHeight();
        var eye=BlockPos.containing(minecraft.player.getX(),minecraft.player.getEyeY(),minecraft.player.getZ());
        var eyeFluid=minecraft.level.getFluidState(eye).getType();
        if (eyeFluid==SiftFluids.STILL || eyeFluid==SiftFluids.FLOWING)
            graphics.fill(0,0,width,height,0x38051A33);
        long time=minecraft.level.getGameTime();
        int block=Math.max(3,width/80);
        // Corner flames occupy at most 7% of the screen height; the center,
        // crosshair and third-person camera remain unobstructed.
        for(int i=0;i<=width/block;i++) {
            int x=i*block;
            double distance=Math.abs(x-width*.5)/(width*.5);
            if (distance < .60) continue;
            double wave=Math.sin(i*.96+time*.26)+.4*Math.cos(i*1.73-time*.15);
            int flame=Math.max(2,(int)(height*.018+height*.009*wave));
            int edge=(int)(height*.020*distance);
            int y=height-flame-edge;
            int core=(i%3==0)?0x6041E8FF:0x503BAAFF;
            graphics.fill(x,y+block,x+block,height,0x451761EB);
            graphics.fill(x+block/4,y,x+block*3/4,y+block,core);
            if ((i+time/4)%3==0)
                graphics.fill(x+block/3,y-block,x+block*2/3,y,0x7082F5FF);
        }
    }
}

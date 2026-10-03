package fr.mathsift.sift;

import net.fabricmc.fabric.api.creativetab.v1.CreativeModeTabEvents;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.item.BucketItem;
import net.minecraft.world.item.CreativeModeTabs;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.LiquidBlock;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.FlowingFluid;
import net.minecraft.world.level.material.Fluid;

public final class SiftFluids {
    private static ResourceKey<Fluid> fluidKey(String name) {
        return ResourceKey.create(Registries.FLUID, SiftMod.id(name));
    }
    public static final FlowingFluid FLOWING = Registry.register(
        BuiltInRegistries.FLUID, fluidKey("flowing_prismatic_tide"), new PrismaticTideFluid.Flowing());
    public static final FlowingFluid STILL = Registry.register(
        BuiltInRegistries.FLUID, fluidKey("prismatic_tide"), new PrismaticTideFluid.Source());

    private static final ResourceKey<Block> BLOCK_KEY =
        ResourceKey.create(Registries.BLOCK, SiftMod.id("prismatic_tide_block"));
    public static final Block BLOCK = Registry.register(BuiltInRegistries.BLOCK, BLOCK_KEY,
        new LiquidBlock(STILL, BlockBehaviour.Properties.ofFullCopy(Blocks.WATER).setId(BLOCK_KEY)));

    private static final ResourceKey<Item> BUCKET_KEY =
        ResourceKey.create(Registries.ITEM, SiftMod.id("prismatic_tide_bucket"));
    public static final Item BUCKET = Registry.register(BuiltInRegistries.ITEM, BUCKET_KEY,
        new BucketItem(STILL, new Item.Properties().craftRemainder(Items.BUCKET)
            .stacksTo(1).setId(BUCKET_KEY)));

    public static void initialize() {
        CreativeModeTabEvents.modifyOutputEvent(CreativeModeTabs.TOOLS_AND_UTILITIES)
            .register(tab -> tab.accept(BUCKET));
    }
    private SiftFluids() {}
}

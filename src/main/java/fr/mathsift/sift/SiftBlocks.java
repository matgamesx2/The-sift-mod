package fr.mathsift.sift;

import java.util.LinkedHashMap;
import java.util.Map;
import net.fabricmc.fabric.api.creativetab.v1.CreativeModeTabEvents;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.references.BlockItemId;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.CreativeModeTabs;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;

public final class SiftBlocks {
    public static final Map<String, Block> BLOCKS = new LinkedHashMap<>();
    private static void add(String name, SoundType sound, float strength, int light, boolean decorative) {
        var identifier = SiftMod.id(name);
        BlockItemId keys = BlockItemId.create(identifier, identifier);
        BlockBehaviour.Properties props = BlockBehaviour.Properties.of().strength(strength).sound(sound);
        if (light > 0) props = props.lightLevel(state -> light);
        if (decorative) props = props.noCollision().noOcclusion().instabreak();
        ResourceKey<Block> blockId = keys.block();
        Block block = Registry.register(BuiltInRegistries.BLOCK, blockId, new Block(props.setId(blockId)));
        Registry.register(BuiltInRegistries.ITEM, keys.item(),
                new BlockItem(block, new Item.Properties().useBlockDescriptionPrefix().setId(keys.item())));
        BLOCKS.put(name, block);
    }
    public static void initialize() {
        add("meadow_soil", SoundType.GRASS, 0.6f, 0, false);
        add("red_growth", SoundType.WART_BLOCK, 1.0f, 0, false);
        add("carapace_stone", SoundType.DEEPSLATE, 1.8f, 0, false);
        add("luminous_relic", SoundType.AMETHYST, 1.2f, 12, false);
        add("teal_turf", SoundType.GRASS, 0.7f, 0, false);
        add("sift_ochre", SoundType.SAND, 0.55f, 0, false);
        add("carapace_shale", SoundType.DEEPSLATE, 1.8f, 0, false);
        add("fossil_rib", SoundType.BONE_BLOCK, 1.6f, 0, false);
        add("lumen_cluster", SoundType.AMETHYST, 1.2f, 10, false);
        add("red_canopy", SoundType.WART_BLOCK, 0.65f, 0, false);
        add("spore_mat", SoundType.MOSS, 0.65f, 0, false);
        add("ichor_crust", SoundType.AMETHYST, 1.1f, 0, false);
        add("meadow_reed", SoundType.GRASS, 0.0f, 0, true);
        add("scarlet_sprout", SoundType.GRASS, 0.0f, 0, true);
        add("carapace_spire", SoundType.STONE, 1.4f, 0, false);
        add("soul_bloom", SoundType.GRASS, 0.0f, 10, true);
        add("scarlet_trunk", SoundType.WOOD, 1.4f, 0, false);
        CreativeModeTabEvents.modifyOutputEvent(CreativeModeTabs.BUILDING_BLOCKS).register(tab -> {
            for (Block block : BLOCKS.values()) tab.accept(block.asItem());
        });
    }
    private SiftBlocks() {}
}

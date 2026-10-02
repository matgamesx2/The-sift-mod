package fr.mathsift.sift;

import java.util.LinkedHashMap;
import java.util.Map;
import net.fabricmc.fabric.api.creativetab.v1.CreativeModeTabEvents;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.item.CreativeModeTabs;
import net.minecraft.world.item.Item;

public final class SiftItems {
    public static final Map<String, Item> ITEMS = new LinkedHashMap<>();
    private static void add(String name, int stackSize) {
        ResourceKey<Item> id = ResourceKey.create(Registries.ITEM, SiftMod.id(name));
        Item item = Registry.register(BuiltInRegistries.ITEM, id,
                new Item(new Item.Properties().stacksTo(stackSize).setId(id)));
        ITEMS.put(name, item);
    }
    public static void initialize() {
        add("lumen_shard", 64);
        add("fossil_fragment", 64);
        add("scarlet_seed", 64);
        add("sift_compass_core", 16);
        CreativeModeTabEvents.modifyOutputEvent(CreativeModeTabs.INGREDIENTS).register(tab -> {
            for (Item item : ITEMS.values()) tab.accept(item);
        });
    }
    private SiftItems() {}
}

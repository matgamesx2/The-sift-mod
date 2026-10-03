package fr.mathsift.sift;

import net.fabricmc.api.ModInitializer;
import net.minecraft.resources.Identifier;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public final class SiftMod implements ModInitializer {
    public static final String MOD_ID = "sift";
    private static final Logger LOG = LoggerFactory.getLogger(MOD_ID);
    public static Identifier id(String name) {
        return Identifier.fromNamespaceAndPath(MOD_ID, name);
    }
    @Override public void onInitialize() {
        SiftBlocks.initialize();
        SiftItems.initialize();
        SiftFluids.initialize();
        LOG.info("THE SIFT: 17 blocks, 4 exploration items and 1 custom prismatic fluid loaded");
    }
}

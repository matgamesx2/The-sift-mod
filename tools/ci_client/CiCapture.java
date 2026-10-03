package fr.mathsift.sift;

import java.nio.file.Files;
import java.nio.file.Path;
import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents;
import net.minecraft.client.Screenshot;

/** Added only to the CI client checkout; never included in the released mod. */
public final class CiCapture implements ClientModInitializer {
    @Override public void onInitializeClient() {
        ClientTickEvents.END_CLIENT_TICK.register(client -> {
            Path request=Path.of("visual", "capture.request");
            if (client.level==null || client.player==null || !Files.exists(request)) return;
            try {
                String name=Files.readString(request).trim();
                if (!name.matches("[a-zA-Z0-9-]+")) throw new IllegalArgumentException("Invalid capture name");
                Files.delete(request);
                Screenshot.takeScreenshot(client.gameRenderer.mainRenderTarget(), image -> {
                    try {
                        image.writeToFile(Path.of("visual",name+".png"));
                        Files.writeString(Path.of("visual",name+".ready"),
                            client.level.dimension()+" "+client.player.getX()+","+
                            client.player.getY()+","+client.player.getZ());
                    } catch (Exception failure) {
                        throw new RuntimeException("Internal game capture failed",failure);
                    }
                });
            } catch (Exception failure) {
                throw new RuntimeException("CI screenshot request failed",failure);
            }
        });
    }
}

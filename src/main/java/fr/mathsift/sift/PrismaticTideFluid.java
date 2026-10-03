package fr.mathsift.sift;

import java.util.Optional;
import java.util.Map;
import java.util.WeakHashMap;
import org.jspecify.annotations.Nullable;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.InsideBlockEffectApplier;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.LiquidBlock;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.material.FlowingFluid;
import net.minecraft.world.level.material.Fluid;
import net.minecraft.world.level.material.FluidState;

/**
 * Genuine, flowable Sift fluid. The rainbow colors are rendered by the Fabric client
 * and SOUL_FIRE_FLAME particles create a blue-burning effect. Vanilla fire ticks
 * would render orange, so blue flames and damage are handled independently.
 */
public abstract class PrismaticTideFluid extends FlowingFluid {
    // entityInside can run for several overlapping fluid cells in one tick.
    // Weak keys keep this deduplication from retaining unloaded entities.
    private static final Map<Entity, Long> LAST_CONTACT = new WeakHashMap<>();
    @Override public Fluid getSource() { return SiftFluids.STILL; }
    @Override public Fluid getFlowing() { return SiftFluids.FLOWING; }
    @Override public boolean isSame(Fluid fluid) {
        return fluid == SiftFluids.STILL || fluid == SiftFluids.FLOWING;
    }
    @Override public Item getBucket() { return SiftFluids.BUCKET; }
    @Override protected BlockState createLegacyBlock(FluidState state) {
        return SiftFluids.BLOCK.defaultBlockState().setValue(LiquidBlock.LEVEL, getLegacyLevel(state));
    }
    @Override protected boolean canConvertToSource(ServerLevel world) { return false; }
    @Override protected void beforeDestroyingBlock(LevelAccessor world, BlockPos pos, BlockState state) {
        BlockEntity blockEntity = state.hasBlockEntity() ? world.getBlockEntity(pos) : null;
        Block.dropResources(state, world, pos, blockEntity);
    }
    @Override public void animateTick(Level world, BlockPos pos, FluidState state, RandomSource random) {
        if (!world.getBlockState(pos.above()).isAir()) return;
        double surface=pos.getY()+state.getHeight(world,pos)+0.05;
        if (random.nextInt(28) == 0) {
            world.addParticle(ParticleTypes.SOUL,
                pos.getX() + random.nextDouble(), surface,
                pos.getZ() + random.nextDouble(), 0.0, 0.05, 0.0);
        }
        if (random.nextInt(64) == 0) {
            world.addParticle(ParticleTypes.SOUL_FIRE_FLAME,
                pos.getX() + random.nextDouble(), surface,
                pos.getZ() + random.nextDouble(), 0.0, 0.035, 0.0);
        }
    }
    @Nullable @Override public ParticleOptions getDripParticle() { return ParticleTypes.SOUL; }
    @Override protected void entityInside(Level level, BlockPos pos, Entity entity,
                                          InsideBlockEffectApplier handler) {
        if (!(level instanceof ServerLevel server)) return;
        long tick=server.getGameTime();
        Long previous=LAST_CONTACT.put(entity,tick);
        if (previous != null && previous.longValue()==tick) return;
        if (tick % 5 == 0) {
            server.sendParticles(ParticleTypes.SOUL_FIRE_FLAME, entity.getX(),
                entity.getY() + entity.getBbHeight() * 0.30, entity.getZ(),
                3, 0.21, entity.getBbHeight() * 0.20, 0.21, 0.014);
        }
        if (server.getGameTime() % 20 == 0 && !entity.fireImmune()) {
            // Real burn damage without vanilla fire ticks (which render red flames).
            entity.hurtServer(server, level.damageSources().magic(), 2.0f);
        }
    }
    @Override protected int getSlopeFindDistance(LevelReader world) { return 4; }
    @Override public int getDropOff(LevelReader world) { return 1; }
    @Override public int getTickDelay(LevelReader world) { return 6; }
    @Override public boolean canBeReplacedWith(FluidState state, BlockGetter world, BlockPos pos,
                                               Fluid fluid, Direction direction) {
        return direction == Direction.DOWN && !isSame(fluid);
    }
    @Override protected float getExplosionResistance() { return 100f; }
    @Override public Optional<SoundEvent> getPickupSound() { return Optional.of(SoundEvents.BUCKET_FILL); }

    public static final class Flowing extends PrismaticTideFluid {
        @Override protected void createFluidStateDefinition(StateDefinition.Builder<Fluid,FluidState> b) {
            super.createFluidStateDefinition(b);
            b.add(LEVEL);
        }
        @Override public int getAmount(FluidState state) { return state.getValue(LEVEL); }
        @Override public boolean isSource(FluidState state) { return false; }
    }
    public static final class Source extends PrismaticTideFluid {
        @Override public int getAmount(FluidState state) { return 8; }
        @Override public boolean isSource(FluidState state) { return true; }
    }
}

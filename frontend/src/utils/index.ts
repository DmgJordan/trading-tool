/**
 * Barrel exports pour compatibilité legacy
 *
 * ⚠️ DÉPRÉCIÉ : Utiliser les imports directs depuis @/shared/lib/*
 *
 * Exemples :
 * - import { formatPrice } from '@/shared/lib/formatters'
 * - import { getStatusColor } from '@/shared/lib/ui'
 *
 * Ce fichier sera supprimé lors de la prochaine phase de refactorisation.
 */

// Ré-exports pour compatibilité uniquement
export * from '@/shared/lib/formatters';
export * from '@/shared/lib/api-helpers';
export * from '@/shared/lib/ui';
export * from './validators';

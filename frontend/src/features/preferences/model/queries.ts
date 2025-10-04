import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { preferencesApi } from '@/services/api';
import type {
  TradingPreferences,
  TradingPreferencesDefault,
  PreferencesValidationInfo,
  TradingPreferencesUpdate,
} from './types';

const preferencesKey = ['preferences', 'current'];
const defaultsKey = ['preferences', 'defaults'];
const validationKey = ['preferences', 'validation'];

export const usePreferencesQuery = () =>
  useQuery<TradingPreferences>({
    queryKey: preferencesKey,
    queryFn: () => preferencesApi.getPreferences(),
    staleTime: 60_000,
  });

export const usePreferencesDefaults = () =>
  useQuery<TradingPreferencesDefault>({
    queryKey: defaultsKey,
    queryFn: () => preferencesApi.getDefaults(),
    staleTime: Infinity,
  });

export const usePreferencesValidation = () =>
  useQuery<PreferencesValidationInfo>({
    queryKey: validationKey,
    queryFn: () => preferencesApi.getValidationInfo(),
    staleTime: Infinity,
  });

export const useUpdatePreferences = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: TradingPreferencesUpdate) =>
      preferencesApi.updatePreferences(payload),
    onSuccess: data => {
      queryClient.setQueryData(preferencesKey, data);
      queryClient.invalidateQueries({ queryKey: preferencesKey });
    },
  });
};

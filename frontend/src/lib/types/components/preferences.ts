/**
 * Types pour les composants de préférences
 */

import { SliderConfig } from '../preferences';

// Range Slider
export interface RangeSliderProps {
  value: number;
  onChange: (value: number) => void;
  config: SliderConfig;
  label: string;
  description?: string;
  error?: string;
  disabled?: boolean;
  showValue?: boolean;
  className?: string;
}

// Radio Card Group
export interface RadioOption {
  value: string;
  label: string;
  description?: string;
  icon?: string;
}

export interface RadioCardGroupProps {
  value: string;
  onChange: (value: string) => void;
  options: RadioOption[];
  label: string;
  description?: string;
  error?: string;
  disabled?: boolean;
  className?: string;
}

// Toggle Switch
export interface ToggleSwitchProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label: string;
  description?: string;
  disabled?: boolean;
  className?: string;
}

// Multi Select
export interface MultiSelectOption {
  value: string;
  label: string;
  disabled?: boolean;
}

export interface MultiSelectProps {
  value: string[];
  onChange: (value: string[]) => void;
  options: MultiSelectOption[];
  label: string;
  description?: string;
  error?: string;
  disabled?: boolean;
  className?: string;
  maxSelections?: number;
}

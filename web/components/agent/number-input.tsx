'use client';

import React from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { MinusIcon, PlusIcon } from 'lucide-react';

interface NumberInputProps {
  value: number;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
  step?: number;
  disabled?: boolean;
  label?: string;
}

export const NumberInput: React.FC<NumberInputProps> = ({
  value,
  onChange,
  min = 1,
  max = 100000,
  step = 1,
  disabled = false,
  label
}) => {
  const increment = () => {
    if (value + step <= max) {
      onChange(value + step);
    }
  };

  const decrement = () => {
    if (value - step >= min) {
      onChange(value - step);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = parseInt(e.target.value, 10);
    if (!isNaN(newValue) && newValue >= min && newValue <= max) {
      onChange(newValue);
    }
  };

  return (
    <div className="space-y-1">
      {label && <p className="text-xs font-medium text-muted-foreground">{label}</p>}
      <div className="flex items-center">
        <Button
          type="button"
          variant="outline"
          size="icon"
          className="h-9 w-9 rounded-r-none"
          onClick={decrement}
          disabled={disabled || value <= min}
        >
          <MinusIcon className="h-3 w-3" />
        </Button>
        <Input
          type="number"
          value={value}
          onChange={handleChange}
          className="h-9 rounded-none text-center [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
          disabled={disabled}
          min={min}
          max={max}
          step={step}
        />
        <Button
          type="button"
          variant="outline"
          size="icon"
          className="h-9 w-9 rounded-l-none"
          onClick={increment}
          disabled={disabled || value >= max}
        >
          <PlusIcon className="h-3 w-3" />
        </Button>
      </div>
    </div>
  );
}; 
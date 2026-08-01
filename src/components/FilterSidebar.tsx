"use client";
import React from 'react';
import * as Checkbox from '@radix-ui/react-checkbox';
import * as Slider from '@radix-ui/react-slider';
import { Check } from 'lucide-react';
import styles from './FilterSidebar.module.css';

export default function FilterSidebar({ onFilterChange }: { onFilterChange?: (filters: any) => void }) {
  const [duration, setDuration] = React.useState([72]);

  return (
    <aside className={styles.sidebar}>
      <h2 className={styles.title}>Filters</h2>
      
      <div className={styles.filterSection}>
        <h3 className={styles.sectionTitle}>Format</h3>
        
        <div className={styles.checkboxWrapper}>
          <Checkbox.Root className={styles.checkboxRoot} id="c1">
            <Checkbox.Indicator className={styles.checkboxIndicator}>
              <Check size={14} />
            </Checkbox.Indicator>
          </Checkbox.Root>
          <label className={styles.label} htmlFor="c1">In-Person</label>
        </div>
        
        <div className={styles.checkboxWrapper}>
          <Checkbox.Root className={styles.checkboxRoot} id="c2">
            <Checkbox.Indicator className={styles.checkboxIndicator}>
              <Check size={14} />
            </Checkbox.Indicator>
          </Checkbox.Root>
          <label className={styles.label} htmlFor="c2">Online</label>
        </div>
      </div>

      <div className={styles.filterSection}>
        <h3 className={styles.sectionTitle}>Max Duration ({duration[0]}h)</h3>
        <Slider.Root className={styles.sliderRoot} value={duration} onValueChange={setDuration} max={120} step={12}>
          <Slider.Track className={styles.sliderTrack}>
            <Slider.Range className={styles.sliderRange} />
          </Slider.Track>
          <Slider.Thumb className={styles.sliderThumb} aria-label="Duration" />
        </Slider.Root>
      </div>
    </aside>
  );
}

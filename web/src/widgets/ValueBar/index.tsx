import { useState } from "react";
import styles from "./index.module.scss";

type OptionsProps = {
  label: string;
  min: number;
  max: number;
  default_value: number;
  onChange: (value: number) => void;
  disable: boolean;
};

export default function ValueBar({ label, min, max, default_value, onChange, disable}: OptionsProps) {
  const [value, setValue] = useState<number>(default_value);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = Number(e.target.value);
    setValue(newValue);
    onChange(newValue);
  };

  return (
    <div id={label + "_valueBar"} className={styles.wrapper}>
      <label className={`${styles.label} ${styles.disable}`}>{label}</label>
      <input
        id={label + "_input"}
        className={styles.bar}
        value={value}
        type="range"
        min={min}
        max={max}
        onChange={handleChange}
        disabled={disable}
      />
      <label className={`${styles.value} ${styles.disable}`}>{value}</label>
    </div>
  );
}
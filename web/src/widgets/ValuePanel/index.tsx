import styles from "./index.module.scss";

type ValueItem = { label: string; value: string | number | boolean | null };

type ValuePanelProps = {
  title: string;
  values: ValueItem[];
  display: "row" | "column";
};

export default function ValuePanel({ title, values, display }: ValuePanelProps) {
  return (
    <div className={styles.wrapper}>
      <fieldset className={`${styles.fieldset} ${display == "column" ? styles.column : styles.row}`}>
        <legend className={styles.legend}>{title}</legend>
        {values.map(({ label, value }) => {
          let displayValue: string;

          if (value === null || value === undefined) {
            displayValue = "—";
          } else if (typeof value === "boolean") {
            displayValue = value ? "Yes" : "No";
          } else {
            displayValue = value.toString();
          }

          return (
            <div key={label} className={styles.valueBox} id={label}>
              <label className={styles.label}>{label + ": "}</label>
              <label className={styles.value}>{displayValue}</label>
            </div>
          );
        })}
      </fieldset>
    </div>
  );
}
import styles from "./index.module.scss";

type ValueBarProps = {
   label: string;
   min: number;
   max: number;
   value: number;
   onChange: (value: number) => void;
   disable: boolean;
};

export default function ValueBar({ label, min, max, value, onChange, disable}: ValueBarProps) {

   	const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
   	   const newValue = Number(e.target.value);
   	   onChange(newValue);
   	};

  	return (
  	  	<div id={label + "_valueBar"} className={styles.wrapper}>
  	  	  	<label className={`${styles.label} ${disable ? styles.disable : ""}`}>{label}</label>
  	  	  	<div className={styles.inputField}>
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
  	  	</div>
  	);
}
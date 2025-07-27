import { useState } from "react";
import styles from "./index.module.scss"

type OptionsProps = {
    label: string;
    options: string[];
    default_option: string;
    onChange: (newOption: string) => void
};

export default function Options({label, options, default_option, onChange} : OptionsProps) {
    const [currentOption, setCurrentOption] = useState<string>(default_option)

    function onOptionChange(newOption: string) {
        setCurrentOption(newOption);
        onChange(newOption);
    }

    return(
        <div id={label+"_options"} className={styles.wrapper}>
            {options.map((option)=>{
                return (
                    <div className={styles.options} id={"option_"+option}>
                        <input
                          className={styles.radio}
                          id={option + "_radio"}
                          type="radio"
                          name={label + "_radio_group"}
                          checked={option === currentOption}
                          onChange={() => onOptionChange(option)}
                        />
                        <a className={styles.label}>{option}</a>
                    </div>
                )
            })}
        </div>
    );
}
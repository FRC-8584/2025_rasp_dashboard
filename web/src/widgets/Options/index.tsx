import { useState } from "react";
import styles from "./index.module.scss"

type OptionsProps = {
    label: string;
    options: string[];
    default_option: string;
    onChange: (newOption: string) => void;
    disable: boolean;
};

export default function Options({label, options, default_option, onChange, disable} : OptionsProps) {
    const [currentOption, setCurrentOption] = useState<string>(default_option)

    function onOptionChange(newOption: string) {
        setCurrentOption(newOption);
        onChange(newOption);
    }

    return(
        <div id={label+"_options"} className={styles.wrapper}>
            <label className={styles.label}>{label}</label>
            <div className={styles.options}>
                {options.map((option)=>{
                    return (
                        <div className={styles.option} id={"option_"+option}>
                            <input
                              className={styles.radio}
                              id={option + "_radio"}
                              type="radio"
                              checked={option === currentOption}
                              onChange={() => onOptionChange(option)}
                              disabled={disable}
                            />
                            <label className={styles.label}>{option}</label>
                        </div>
                    )
                })}
            </div>
        </div>
    );
}
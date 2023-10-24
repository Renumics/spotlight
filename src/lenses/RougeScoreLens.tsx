import { Lens } from "../types";
import rouge from 'rouge';

const calculateRougeScore=(values: unknown[])=>{
        return rouge.n(values[0], values[1])
    // return 0;
}

const RougeScoreLens: Lens = ({values})=>{
    const result = calculateRougeScore(values)
    return (<>Rouge score: {result}</>)
}

RougeScoreLens.key="RougeScoreView"
RougeScoreLens.dataTypes=["str"]
RougeScoreLens.defaultHeight = 48
RougeScoreLens.minHeight=22
RougeScoreLens.maxHeight=512
RougeScoreLens.multi=true
RougeScoreLens.displayName="ROUGE Score"
RougeScoreLens.filterAllowedColumns=(allColumns, selectedColumns) => {
    if(selectedColumns.length===2)
        return selectedColumns
    else return allColumns.filter(({type}) => type.kind === 'str')
};
export default RougeScoreLens

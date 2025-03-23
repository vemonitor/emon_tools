import { GraphHelper } from '@/helpers/graphHelper';
import { timeFormat, utcFormat } from 'd3-time-format';
import { HTMLAttributes, PropsWithChildren } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import clsx from 'clsx';

type ChartInfoItemProps = PropsWithChildren<{
  title: string;
}>

const ChartInfoItem = ({
  title,
  children
}: ChartInfoItemProps) => {
  return (
    <div>
      <div>{title}:</div>
      <div
        className='pl-2'
      >{children}</div>
    </div>
  )
}

type TwoColsLabelProps = {
  label: string;
  value: string;
  classBody?: string;
  classLabel?: string;
  classValue?: string
}

const TwoColsLabelItem = ({
  label,
  value,
  classBody,
  classLabel,
  classValue
}: TwoColsLabelProps) => {
  return (
    <div
      className={clsx(
        'grid grid-cols-3',
        classBody
      )}
    >
      <div
        className={clsx(
          '',
          classLabel
        )}
      >{label}:</div>
      <div
        className={clsx(
          'col-span-2',
          classValue
        )}
      >{value}</div>
    </div>
  )
}

type ChartInfoProps = HTMLAttributes<HTMLDivElement> & {
  currentDomain: Date[];
}

const ChartInfo = ({
  currentDomain
}: ChartInfoProps) => {
  const is_domain = currentDomain.length === 2
  const formatDateUtc = utcFormat("%a %d %b %Y %H:%M:%S")
  const formatDate = timeFormat("%a %d %b %Y %H:%M:%S")
  return(
    <div>
      {is_domain ? (
        <Card className="w-[350px]">
          <CardHeader
            className='border-b-2 p-3'
          >
            <CardTitle>Graph Meta</CardTitle>
          </CardHeader>
          <CardContent
            className='px-3'
          >
            <ChartInfoItem
              title='Current Window'
            >
              <ChartInfoItem
                title='From'
              >
                <TwoColsLabelItem 
                  label='Utc'
                  value={formatDateUtc(currentDomain[0])}
                />
                <TwoColsLabelItem 
                  label='Local'
                  value={formatDate(currentDomain[0])}
                />
                <TwoColsLabelItem 
                  label='Time'
                  value={`${currentDomain[0].getTime() / 1000}`}
                />
              </ChartInfoItem>
              <ChartInfoItem
                title='To'
              >
                <TwoColsLabelItem 
                  label='Utc'
                  value={formatDateUtc(currentDomain[1])}
                />
                <TwoColsLabelItem 
                  label='Local'
                  value={formatDate(currentDomain[1])}
                />
                <TwoColsLabelItem 
                  label='Time'
                  value={`${currentDomain[1].getTime() / 1000}`}
                />
              </ChartInfoItem>
              <ChartInfoItem
                title='Length'
              >
                <div>
                  {GraphHelper.formatDuration(currentDomain[0], currentDomain[1])}
                </div>
                <div>
                  {(currentDomain[1].getTime() - currentDomain[0].getTime())/ 1000} s
                </div>
              </ChartInfoItem>
            </ChartInfoItem>
            
          </CardContent>
        </Card>
      ) : (null)}
    </div>
  )
};

export default ChartInfo;

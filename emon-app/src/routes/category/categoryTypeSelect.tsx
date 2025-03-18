import {
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
  } from '@/components/ui/form';

import {
    Select,
    SelectContent,
    SelectGroup,
    SelectItem,
    SelectTrigger,
    SelectValue
  } from "@/components/ui/select";

import { Control, FieldValues } from 'react-hook-form';

interface CategoryTypeSelectProps {
  form: {
    control: Control<FieldValues>;
  };
  field: unknown;
}

export default function categoryTypeSelect({
    form
}: CategoryTypeSelectProps) {
  return (
    <FormField
        control={form.control}
        name="emonhost_id"
        render={({ field }) => (
        <FormItem>
            <FormLabel>Emon Host</FormLabel>
            <FormControl>
            <Select
                defaultValue={field?.value ? field?.value.toString() : "0"}
                onValueChange={field.onChange}
            >
                <SelectTrigger className="w-[180px]">
                    <SelectValue placeholder="Emoncms Host" />
                </SelectTrigger>
                <SelectContent>
                    <SelectGroup>
                        <SelectItem value="0">Undefined</SelectItem>
                        <SelectItem value="1">Fina Files</SelectItem>
                        <SelectItem value="2">Fina Paths</SelectItem>
                    </SelectGroup>
                </SelectContent>
            </Select>
            </FormControl>
            <FormMessage />
        </FormItem>
        )}
    />
  )
}

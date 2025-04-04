import { Check, ChevronsUpDown } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
    Command,
    CommandEmpty,
    CommandGroup,
    CommandInput,
    CommandItem,
    CommandList,
} from "@/components/ui/command"
import {
    FormControl,
    FormDescription,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form"
import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from "@/components/ui/popover"
import { useAuth } from "@/hooks/use-auth"
import { useQuery } from "@tanstack/react-query"
import { Loader } from "@/components/layout/loader"

type ComboBox = {
    name: string,
    label: string,
    description: string,
    url: string,
    queryKey: readonly unknown[],
    resultKeyLabel: string,
    resultKeyValue: string,
    is_dialog?: boolean,
    form,
    field
}

export default function ComboBox({
    name,
    label,
    description,
    url,
    queryKey,
    resultKeyLabel,
    resultKeyValue,
    is_dialog,
    form,
    field
}: ComboBox) {
    const { fetchWithAuth } = useAuth();

    const queryResult = useQuery(
        {
            queryKey: queryKey,
            retry: false,
            refetchOnMount: 'always',  // Always refetch when the component mounts
            queryFn: () =>
                fetchWithAuth(
                    url,
                    {
                        method: 'GET',
                    }
                ).then((response) => response.json()),
        }
    );
    if (queryResult.isPending) {
        return (<Loader />)
    }
    return (
        <FormItem className="flex flex-col">
            <FormLabel>{label}</FormLabel>
            <Popover modal={is_dialog ?? false}>
                <PopoverTrigger asChild>
                    <FormControl>
                        <Button
                            variant="outline"
                            role="combobox"
                            className={cn(
                                "w-[200px] justify-between",
                                !field.value && "primary"
                            )}
                        >
                            {queryResult.isPending ? (
                                <Loader />
                            ) : queryResult.isError || !(queryResult.data && queryResult.data.data) ? (
                                `Select ${label}`
                            ) : (
                                <>
                                    {field.value ? queryResult.data.data.find(
                                            (fieldItem) => fieldItem[resultKeyValue] === field.value
                                        )?.[resultKeyLabel]
                                        : `Select ${label}`
                                    }
                                </>
                            )}

                            <ChevronsUpDown className="opacity-50" />
                        </Button>
                    </FormControl>
                </PopoverTrigger>
                <PopoverContent className="w-[200px] p-0">
                    <Command>
                        <CommandInput
                            placeholder={`Search ${label}`}
                            className="h-9"
                        />
                        <CommandList>
                            <CommandEmpty>No framework found.</CommandEmpty>
                            <CommandGroup>
                                {queryResult.isPending ? (
                                    <Loader />
                                ) : queryResult.isError || !(queryResult.data && queryResult.data.data) ? (
                                    `Select ${label}`
                                ) : (
                                    <>
                                        {queryResult.data.data.map((fieldItem, index) => (
                                            <CommandItem
                                                value={fieldItem[resultKeyValue]}
                                                key={index}
                                                onSelect={() => {
                                                    form.setValue(name, fieldItem[resultKeyValue])
                                                }}
                                            >
                                                {fieldItem[resultKeyLabel]}
                                                <Check
                                                    className={cn(
                                                        "ml-auto",
                                                        fieldItem[resultKeyValue] === field.value
                                                            ? "opacity-100"
                                                            : "opacity-0"
                                                    )}
                                                />
                                            </CommandItem>
                                        ))}
                                    </>
                                )}

                            </CommandGroup>
                        </CommandList>
                    </Command>
                </PopoverContent>
            </Popover>
            <FormDescription>
                {description}
            </FormDescription>
            <FormMessage />
        </FormItem>
    )
}

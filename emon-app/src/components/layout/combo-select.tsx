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
    Drawer,
    DrawerContent,
    DrawerTrigger,
} from "@/components/ui/drawer"
import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from "@/components/ui/popover"
import { useIsMobile } from "@/hooks/use-mobile"
import { Status } from "@/lib/types"
import { useEffect, useState } from "react"

type ComboBoxResponsiveProps = {
    defaultLabel: string,
    statuses: Status[],
    handleChange?: (status: Status) => void
}

export function ComboBoxResponsive({
    defaultLabel,
    statuses,
    handleChange
}: ComboBoxResponsiveProps) {
    const [open, setOpen] = useState(false)
    const isMobile = useIsMobile()
    const [selectedStatus, setSelectedStatus] = useState<Status | null>(
        null
    )
    useEffect(() => {
        if(handleChange && selectedStatus){
            handleChange(selectedStatus)
        }
      }, [handleChange, selectedStatus]);

    if (!isMobile) {
        return (
            <Popover open={open} onOpenChange={setOpen}>
                <PopoverTrigger asChild>
                    <Button variant="outline" className="w-[200px] justify-start">
                        {selectedStatus ? <>{selectedStatus.label}</> : <>+ Select {defaultLabel}</>}
                    </Button>
                </PopoverTrigger>
                <PopoverContent className="w-[200px] p-0" align="start">
                    <StatusList
                        defaultLabel={defaultLabel}
                        statuses={statuses}
                        setOpen={setOpen}
                        setSelectedStatus={setSelectedStatus}
                    />
                </PopoverContent>
            </Popover>
        )
    }

    return (
        <Drawer open={open} onOpenChange={setOpen}>
            <DrawerTrigger asChild>
                <Button variant="outline" className="w-[150px] justify-start">
                    {selectedStatus ? <>{selectedStatus.label}</> : <>+ Set status</>}
                </Button>
            </DrawerTrigger>
            <DrawerContent>
                <div className="mt-4 border-t">
                    <StatusList
                        defaultLabel={defaultLabel}
                        statuses={statuses}
                        setOpen={setOpen}
                        setSelectedStatus={setSelectedStatus}
                    />
                </div>
            </DrawerContent>
        </Drawer>
    )
}

type StatusListProps = {
    defaultLabel: string
    statuses: Status[]
    setOpen: (open: boolean) => void
    setSelectedStatus: (status: Status | null) => void
}

function StatusList({
    defaultLabel,
    statuses,
    setOpen,
    setSelectedStatus,
}: StatusListProps) {
    const placeholder = defaultLabel ? `Filter ${defaultLabel} ...` : `Filter item...`
    return (
        <Command>
            <CommandInput placeholder={placeholder} />
            <CommandList>
                <CommandEmpty>No results found.</CommandEmpty>
                <CommandGroup>
                    {statuses.map((status) => (
                        <CommandItem
                            key={status.value}
                            value={status.value}
                            onSelect={(value) => {
                                setSelectedStatus(
                                    statuses.find((priority) => priority.value === value) || null
                                )
                                setOpen(false)
                            }}
                        >
                            {status.label}
                        </CommandItem>
                    ))}
                </CommandGroup>
            </CommandList>
        </Command>
    )
}
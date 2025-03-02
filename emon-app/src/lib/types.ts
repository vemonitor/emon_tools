export type SubmitHandlerProps = Promise<{ 
    success: boolean,
    act?: "add" | "edit",
    itemId?: string,
    error?: string,
    msg?: string,
    field?: string,
    redirect?: string
 } | void
>

export type BaseActionErrorType = {
    table?: string,
    field?: string,
    error?: string
}

export type AddActionType = Promise<
  void | {
    success: boolean;
    act?: "add" | "edit";
    itemId?: string;
    from_error?: string;
    error?: string;
    errors?: BaseActionErrorType[];
    msg?: string;
    field?: string;
    redirect?: string;
  }
>

export interface User {
    id: string;
    name: string;
    email?: string;
    avatar?: string
}

export interface EmonHostBase {
    name: string;
    host?: string;
    api_key?: string;
}

export interface EmonHostView extends EmonHostBase{
    name: string;
    host?: string;
    api_key?: string;
}


export interface EmonHostEdit extends EmonHostBase{
    id?: number;
    created_at?: string;
    updated_at?: string;
    owner_id?: string
}

export interface ArchiveGroupBase {
    name: string;
    parent_group_id?: bigint;
}

export interface ArchiveGroupList extends ArchiveGroupBase{
    id?: number;
    owner_id?: string
}

export interface ArchiveGroupEdit extends ArchiveGroupBase{
    id?: number;
    created_at?: string;
    updated_at?: string;
    owner_id?: string
}

export interface ArchiveFileBase {
    name: string;
    file_name: string;
    start_time: string;
    end_time: string;
    interval?: number;
    size?: number;
    npoints?: number;
    feed_id?: bigint;
    sha_256: string;
}

export interface ArchiveFileList extends ArchiveFileBase{
    id?: bigint;
    owner_id?: string
    archivegroup_id?: bigint
    emonhost_id?: bigint
}

export interface ArchiveFileEdit extends ArchiveFileBase{
    id?: bigint;
    created_at?: string;
    updated_at?: string;
    owner_id?: string;
    archivegroup_id?: bigint
    emonhost_id?: bigint
}


enum AnimeType {TV, Movie, OAV, TV-Sp, SMovie, ONA, AMV, Other};
enum LinkType {Auto, AniDB, ANN, MAL, Wikipedia, 'Official page'=6,
    Other=15};
enum UserStatus {None, Want, Now, Done, Dropped, 'Partially watched'};

interface Link {
    url: string;
    type: LinkType;
}

interface Item {
    id: mongodb.ObjectID;
    names: string[];
    genre: string;
    type: AnimeTypes;
    episodes: number;
    duration: number;
    release: DateRange;
    links: Link[];
    bundle: mongodb.ObjectID[];
}

interface UserStatus {
    item: mongodb.ObjectID;
    state: UserStatus;
    count: number;
    rating: number;
    added: Date;
    changed: Date;
}

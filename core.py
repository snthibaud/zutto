from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Optional, FrozenSet


@dataclass(frozen=True)
class Item:
    """
    EN: Represents a single tradeable item with a bilingual name and description. 
        The English and Japanese texts are separated by a slash.
    JP: 英日両言語をスラッシュで区切った名称と説明を持つ単一の取引可能なアイテムを表します。
    
    Example / 例:
    name: "Book/本"
    description: "A mystery novel/ミステリー小説"
    """
    name: str
    description: str = ""


@dataclass(frozen=True)
class User:
    """
    EN: Represents a user holding a set of items. With frozen dataclasses, modifying data 
        returns a new instance.
    JP: アイテム集合を持つユーザーを表します。不変（frozen）データクラスのため、変更時には
        新たなインスタンスを返します。
    """
    username: str
    items: FrozenSet[Item] = field(default_factory=frozenset)

    def with_item_added(self, item: Item) -> "User":
        """
        EN: Returns a new User with the specified item added.
        JP: 指定されたアイテムを追加した新しいUserインスタンスを返します。
        """
        return replace(self, items=self.items.union({item}))

    def with_items_added(self, items: FrozenSet[Item]) -> "User":
        """
        EN: Returns a new User with a set of items added.
        JP: 指定したアイテム集合を追加した新しいUserインスタンスを返します。
        """
        return replace(self, items=self.items.union(items))

    def with_item_removed(self, item: Item) -> "User":
        """
        EN: Returns a new User with the specified item removed.
        JP: 指定したアイテムを削除した新しいUserインスタンスを返します。
        """
        return replace(self, items=self.items.difference({item}))

    def with_items_removed(self, items: FrozenSet[Item]) -> "User":
        """
        EN: Returns a new User with the specified set of items removed.
        JP: 指定したアイテム集合を削除した新しいUserインスタンスを返します。
        """
        return replace(self, items=self.items.difference(items))


# Functional API for Enum
OfferStatus = Enum('OfferStatus', 'PENDING ACCEPTED DECLINED')


@dataclass(frozen=True)
class Offer:
    """
    EN: Represents an offer between two users. User A offers a set of items and requests 
        another set from User B. The offer is immutable, so accept/decline returns new objects.
    
    JP: 2人のユーザー間で行われるオファーを表します。ユーザーAは自分のアイテム集合を提供し、 
        ユーザーBのアイテム集合との交換を望みます。このオファーは不変であり、 
        承諾または却下は新たなオブジェクトを返します。
    """
    user_a: User
    user_b: User
    offered_items: FrozenSet[Item]
    requested_items: FrozenSet[Item]
    status: OfferStatus = OfferStatus.PENDING

    def accept(self) -> tuple["Offer", User, User]:
        """
        EN: Accept the offer if pending and both parties own the correct items. Returns updated 
            Offer and User objects.
        
        JP: オファーが保留中かつ両者が正しいアイテムを所有している場合に承諾し、
            更新後のOfferとUserオブジェクトを返します。
        """
        if self.status != OfferStatus.PENDING:
            return self, self.user_a, self.user_b

        # Check ownership
        if not self.offered_items.issubset(self.user_a.items):
            return self, self.user_a, self.user_b
        if not self.requested_items.issubset(self.user_b.items):
            return self, self.user_a, self.user_b

        # Perform the trade
        updated_user_a = self.user_a.with_items_removed(self.offered_items).with_items_added(self.requested_items)
        updated_user_b = self.user_b.with_items_removed(self.requested_items).with_items_added(self.offered_items)

        updated_offer = replace(self, status=OfferStatus.ACCEPTED, user_a=updated_user_a, user_b=updated_user_b)
        return updated_offer, updated_user_a, updated_user_b

    def decline(self) -> "Offer":
        """
        EN: Decline the offer if it is pending, returning a new Offer with status DECLINED.
        JP: 保留中のオファーを却下し、状態がDECLINEDの新しいOfferを返します。
        """
        if self.status == OfferStatus.PENDING:
            return replace(self, status=OfferStatus.DECLINED)
        return self


# Example usage / 使用例
if __name__ == "__main__":
    # EN: Create items with bilingual names/descriptions using a slash.
    # JP: スラッシュで英日併記された名前と説明を持つアイテムを作成。
    book = Item(name="Book/本", description="A mystery novel/ミステリー小説")
    guitar = Item(name="Guitar/ギター", description="An acoustic guitar/アコースティックギター")
    lamp = Item(name="Lamp/ランプ", description="A vintage lamp/ビンテージのランプ")
    pen = Item(name="Pen/ペン", description="A fancy fountain pen/高級万年筆")

    # EN: Create users with items
    # JP: アイテムを持つユーザーを作成
    alice = User(username="alice", items=frozenset({book, pen}))
    bob = User(username="bob", items=frozenset({guitar, lamp}))

    # EN: Alice wants to trade her book and pen for Bob's guitar and lamp
    # JP: アリスは本とペンをギターとランプと交換したい
    offer = Offer(
        user_a=alice,
        user_b=bob,
        offered_items=frozenset({book, pen}),
        requested_items=frozenset({guitar, lamp})
    )

    # EN: Bob accepts the offer
    # JP: ボブがオファーを承諾
    updated_offer, updated_alice, updated_bob = offer.accept()

    # EN: Print results
    # JP: 結果の表示
    print("Offer status / オファー状態:", updated_offer.status.name)
    print("Alice's items / アリスのアイテム:", [item.name for item in updated_alice.items])
    print("Bob's items / ボブのアイテム:", [item.name for item in updated_bob.items])

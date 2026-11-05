"""Fulu mainnet beacon block containers, as far as a SignedBeaconBlock needs them."""
from ssz_codec import (BitList, BitVector, ByteList, ByteVector, Bytes20, Bytes32, Bytes48,
                       Bytes96, Container, List, Uint64, Uint256, Vector)

Checkpoint = Container("Checkpoint", [("epoch", Uint64), ("root", Bytes32)])
AttestationData = Container("AttestationData", [
    ("slot", Uint64), ("index", Uint64), ("beacon_block_root", Bytes32),
    ("source", Checkpoint), ("target", Checkpoint)])
Attestation = Container("Attestation", [
    ("aggregation_bits", BitList(2048 * 64)), ("data", AttestationData),
    ("signature", Bytes96), ("committee_bits", BitVector(64))])
IndexedAttestation = Container("IndexedAttestation", [
    ("attesting_indices", List(Uint64, 2048 * 64)), ("data", AttestationData),
    ("signature", Bytes96)])
AttesterSlashing = Container("AttesterSlashing", [
    ("attestation_1", IndexedAttestation), ("attestation_2", IndexedAttestation)])
BeaconBlockHeader = Container("BeaconBlockHeader", [
    ("slot", Uint64), ("proposer_index", Uint64), ("parent_root", Bytes32),
    ("state_root", Bytes32), ("body_root", Bytes32)])
SignedBeaconBlockHeader = Container("SignedBeaconBlockHeader", [
    ("message", BeaconBlockHeader), ("signature", Bytes96)])
ProposerSlashing = Container("ProposerSlashing", [
    ("signed_header_1", SignedBeaconBlockHeader), ("signed_header_2", SignedBeaconBlockHeader)])
Eth1Data = Container("Eth1Data", [
    ("deposit_root", Bytes32), ("deposit_count", Uint64), ("block_hash", Bytes32)])
DepositData = Container("DepositData", [
    ("pubkey", Bytes48), ("withdrawal_credentials", Bytes32), ("amount", Uint64),
    ("signature", Bytes96)])
Deposit = Container("Deposit", [("proof", Vector(Bytes32, 33)), ("data", DepositData)])
VoluntaryExit = Container("VoluntaryExit", [("epoch", Uint64), ("validator_index", Uint64)])
SignedVoluntaryExit = Container("SignedVoluntaryExit", [
    ("message", VoluntaryExit), ("signature", Bytes96)])
SyncAggregate = Container("SyncAggregate", [
    ("sync_committee_bits", BitVector(512)), ("sync_committee_signature", Bytes96)])
Withdrawal = Container("Withdrawal", [
    ("index", Uint64), ("validator_index", Uint64), ("address", Bytes20), ("amount", Uint64)])
Transaction = ByteList(2**30)
ExecutionPayload = Container("ExecutionPayload", [
    ("parent_hash", Bytes32), ("fee_recipient", Bytes20), ("state_root", Bytes32),
    ("receipts_root", Bytes32), ("logs_bloom", ByteVector(256)), ("prev_randao", Bytes32),
    ("block_number", Uint64), ("gas_limit", Uint64), ("gas_used", Uint64), ("timestamp", Uint64),
    ("extra_data", ByteList(32)), ("base_fee_per_gas", Uint256), ("block_hash", Bytes32),
    ("transactions", List(Transaction, 2**20)), ("withdrawals", List(Withdrawal, 16)),
    ("blob_gas_used", Uint64), ("excess_blob_gas", Uint64)])
ExecutionPayloadHeader = Container("ExecutionPayloadHeader", [
    ("parent_hash", Bytes32), ("fee_recipient", Bytes20), ("state_root", Bytes32),
    ("receipts_root", Bytes32), ("logs_bloom", ByteVector(256)), ("prev_randao", Bytes32),
    ("block_number", Uint64), ("gas_limit", Uint64), ("gas_used", Uint64), ("timestamp", Uint64),
    ("extra_data", ByteList(32)), ("base_fee_per_gas", Uint256), ("block_hash", Bytes32),
    ("transactions_root", Bytes32), ("withdrawals_root", Bytes32),
    ("blob_gas_used", Uint64), ("excess_blob_gas", Uint64)])
BLSToExecutionChange = Container("BLSToExecutionChange", [
    ("validator_index", Uint64), ("from_bls_pubkey", Bytes48), ("to_execution_address", Bytes20)])
SignedBLSToExecutionChange = Container("SignedBLSToExecutionChange", [
    ("message", BLSToExecutionChange), ("signature", Bytes96)])
DepositRequest = Container("DepositRequest", [
    ("pubkey", Bytes48), ("withdrawal_credentials", Bytes32), ("amount", Uint64),
    ("signature", Bytes96), ("index", Uint64)])
WithdrawalRequest = Container("WithdrawalRequest", [
    ("source_address", Bytes20), ("validator_pubkey", Bytes48), ("amount", Uint64)])
ConsolidationRequest = Container("ConsolidationRequest", [
    ("source_address", Bytes20), ("source_pubkey", Bytes48), ("target_pubkey", Bytes48)])
ExecutionRequests = Container("ExecutionRequests", [
    ("deposits", List(DepositRequest, 8192)), ("withdrawals", List(WithdrawalRequest, 16)),
    ("consolidations", List(ConsolidationRequest, 2))])
BeaconBlockBody = Container("BeaconBlockBody", [
    ("randao_reveal", Bytes96), ("eth1_data", Eth1Data), ("graffiti", Bytes32),
    ("proposer_slashings", List(ProposerSlashing, 16)),
    ("attester_slashings", List(AttesterSlashing, 1)),
    ("attestations", List(Attestation, 8)), ("deposits", List(Deposit, 16)),
    ("voluntary_exits", List(SignedVoluntaryExit, 16)), ("sync_aggregate", SyncAggregate),
    ("execution_payload", ExecutionPayload),
    ("bls_to_execution_changes", List(SignedBLSToExecutionChange, 16)),
    ("blob_kzg_commitments", List(Bytes48, 4096)), ("execution_requests", ExecutionRequests)])
BeaconBlock = Container("BeaconBlock", [
    ("slot", Uint64), ("proposer_index", Uint64), ("parent_root", Bytes32),
    ("state_root", Bytes32), ("body", BeaconBlockBody)])
SignedBeaconBlock = Container("SignedBeaconBlock", [
    ("message", BeaconBlock), ("signature", Bytes96)])
